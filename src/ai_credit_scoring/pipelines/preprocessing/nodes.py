import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


# ----------------- Helpery ----------------- #


def _to_numeric_if_possible(s: pd.Series) -> pd.Series:
    if s.dtype == "object":
        try:
            return pd.to_numeric(s)
        except Exception:
            return s
    return s


def _impute(
    df: pd.DataFrame,
    num_strategy: str,
    cat_strategy: str,
    exclude: set[str],
) -> pd.DataFrame:
    df = df.copy()
    num_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude
    ]
    cat_cols = [
        c for c in df.select_dtypes(exclude=[np.number]).columns if c not in exclude
    ]

    if num_strategy == "median":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].median())
    elif num_strategy == "mean":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].mean())
    else:
        raise ValueError(f"Unknown num_strategy={num_strategy}")

    if cat_strategy == "most_frequent":
        for c in cat_cols:
            mode = df[c].mode(dropna=True)
            fill = mode.iloc[0] if not mode.empty else ""
            df[c] = df[c].fillna(fill)
    else:
        raise ValueError(f"Unknown cat_strategy={cat_strategy}")

    return df


def _clip_outliers(
    df: pd.DataFrame,
    method: str = "iqr",
    iqr_factor: float = 1.5,
    zscore_thresh: float = 3.0,
    exclude: set[str] | None = None,
) -> pd.DataFrame:
    """Ogólny clipping outlierów dla kolumn numerycznych z opcją wykluczeń."""
    df = df.copy()
    exclude = exclude or set()
    num_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude
    ]

    if method == "iqr":
        for c in num_cols:
            q1, q3 = df[c].quantile([0.25, 0.75])
            iqr = q3 - q1
            low, high = q1 - iqr_factor * iqr, q3 + iqr_factor * iqr
            df[c] = df[c].clip(lower=low, upper=high)
    elif method == "zscore":
        for c in num_cols:
            mu, sigma = df[c].mean(), df[c].std(ddof=0)
            if sigma == 0 or np.isnan(sigma):
                continue
            z = (df[c] - mu) / sigma
            df.loc[z > zscore_thresh, c] = mu + zscore_thresh * sigma
            df.loc[z < -zscore_thresh, c] = mu - zscore_thresh * sigma
    else:
        raise ValueError(f"Unknown outlier method={method}")

    return df


# ----------------- Cleaning ----------------- #


def clean_data(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    """
    Główne czyszczenie danych:
    - konwersje typów
    - usuwanie kolumn/wierszy z dużą liczbą braków
    - imputacja braków
    - domenowe przycinanie/usuwanie outlierów (wiek, dochód itd. wg EDA)
    - ogólny clipping IQR (z wykluczeniem wieku)
    - proste feature engineering (binning wieku i dochodu)
    - dodanie stabilnego ID wiersza
    """
    p = params or {}
    target = p.get("target")
    clean_p = p.get("clean", {}) or {}

    col_missing_thresh = float(clean_p.get("col_missing_thresh", 0.6))
    row_missing_thresh = float(clean_p.get("row_missing_thresh", 0.8))
    num_strategy = clean_p.get("num_imputer", "median")
    cat_strategy = clean_p.get("cat_imputer", "most_frequent")

    out_cfg = clean_p.get("outlier", {}) or {}
    out_method = out_cfg.get("method", "iqr")
    iqr_factor = float(out_cfg.get("iqr_factor", 1.5))
    zscore_thresh = float(out_cfg.get("zscore_thresh", 3.0))

    # 1) Konwersja typów (także target, jeśli się da)
    df = df.apply(_to_numeric_if_possible)

    # 2) Usuwanie kolumn/wierszy z nadmiarem NaN
    col_na_ratio = df.isna().mean()
    cols_to_drop = col_na_ratio[col_na_ratio > col_missing_thresh].index.tolist()

    # target nigdy nie może wylecieć
    if target in cols_to_drop:
        cols_to_drop.remove(target)
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    row_na_ratio = df.isna().mean(axis=1)
    rows_to_drop = row_na_ratio[row_na_ratio > row_missing_thresh].index
    if len(rows_to_drop) > 0:
        df = df.drop(index=rows_to_drop)

    # 3) Imputacja (bez targetu)
    exclude = {target} if target else set()
    df = _impute(df, num_strategy, cat_strategy, exclude=exclude)

    # 4) Domenowe przycinanie/usuwanie outlierów na podstawie EDA
    num_cols = df.select_dtypes(include=[np.number]).columns

    # person_age: usuwamy wiersze poza [18, 90] (zbędne dzieci i ekstremalni "dziadkowie")
    if "person_age" in num_cols:
        mask = (df["person_age"] >= 18) & (df["person_age"] <= 90)
        df = df.loc[mask].copy()

    # person_income: clip do 99 percentyla, minimum 0
    if "person_income" in num_cols:
        q_hi = df["person_income"].quantile(0.99)
        df["person_income"] = df["person_income"].clip(lower=0, upper=q_hi)

    # person_emp_length: długość zatrudnienia, nie może być ujemna, 99 percentyl
    if "person_emp_length" in num_cols:
        q_hi = df["person_emp_length"].quantile(0.99)
        df["person_emp_length"] = df["person_emp_length"].clip(lower=0, upper=q_hi)

    # cb_person_cred_hist_length: historia kredytowa w latach, też [0, 99 percentyl]
    if "cb_person_cred_hist_length" in num_cols:
        q_hi = df["cb_person_cred_hist_length"].quantile(0.99)
        df["cb_person_cred_hist_length"] = df["cb_person_cred_hist_length"].clip(
            lower=0, upper=q_hi
        )

    # loan_percent_income: teoretycznie w okolicach 0–1; ograniczamy górę
    if "loan_percent_income" in num_cols:
        q_hi = df["loan_percent_income"].quantile(0.99)
        upper = min(q_hi, 0.8)
        df["loan_percent_income"] = df["loan_percent_income"].clip(lower=0, upper=upper)

    # 5) Ogólny clipping outlierów (IQR / z-score) dla reszty numerycznych
    #    Wiek wykluczamy, żeby nie robić wartości typu 40.5 – wiek będzie int.
    extra_exclude = set(exclude)
    if "person_age" in df.columns:
        extra_exclude.add("person_age")

    df = _clip_outliers(
        df,
        method=out_method,
        iqr_factor=iqr_factor,
        zscore_thresh=zscore_thresh,
        exclude=extra_exclude,
    )

    # 6) Wymuszenie całkowitego wieku (na samym końcu, po wszystkich operacjach)
    if "person_age" in df.columns:
        df["person_age"] = df["person_age"].round().astype("int64")

    # 7) Feature engineering: binning wieku i dochodu

    #    7.1 person_age_bin: stałe przedziały 18–25, 26–35, 36–45, 46–60, 60+
    if "person_age" in df.columns:
        df["person_age_bin"] = pd.cut(
            df["person_age"],
            bins=[18, 25, 35, 45, 60, 120],  # 120 "na zapas", ale i tak mamy max <= 90
            labels=["18-25", "26-35", "36-45", "46-60", "60+"],
            right=True,
            include_lowest=True,
        )
        df["person_age_bin"] = df["person_age_bin"].astype("category")

    #    7.2 person_income_bin: kwantyle z mocniejszym rozbiciem góry
    if "person_income" in df.columns:
        try:
            quantiles = df["person_income"].quantile(
                [0.0, 0.2, 0.4, 0.6, 0.8, 0.95, 1.0]
            ).values
            quantiles = np.unique(quantiles)
            if len(quantiles) >= 2:
                df["person_income_bin"] = pd.cut(
                    df["person_income"],
                    bins=quantiles,
                    include_lowest=True,
                )
                df["person_income_bin"] = df["person_income_bin"].astype("category")
        except Exception:
            # w razie patologii z kwantylami – po prostu nie tworzymy binu dochodu
            pass

    # 8) Stabilny identyfikator wiersza do kontroli przecieków
    id_col = (params or {}).get("id_col", "_row_id")
    if id_col not in df.columns:
        df = df.reset_index(drop=True)
        df[id_col] = df.index.astype(int)

    return df


# ----------------- Scaling ----------------- #


def scale_data(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    """
    StandardScaler dla wszystkich numerycznych,
    z wyłączeniem targetu i kolumny ID.
    """
    p = params or {}
    target = p.get("target")
    id_col = p.get("id_col", "_row_id")

    df = df.copy()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in [target, id_col]:
        if col in num_cols:
            num_cols.remove(col)

    if num_cols:
        scaler = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])

    return df


# ----------------- Split ----------------- #


def split_data(df: pd.DataFrame, params: dict | None = None):
    """
    Podział na train / val / test:
    - jeśli mamy target: stratified split 70 / 15 / 15
    - jeśli nie: prosty podział losowy
    """
    p = params or {}
    target = p.get("target")

    if target and target in df.columns:
        # najpierw test 15% (stratyfikowany), potem z reszty walidacja 15%
        train_val, test = train_test_split(
            df, test_size=0.15, random_state=42, stratify=df[target]
        )
        rel_val = 0.15 / (1.0 - 0.15)
        train, val = train_test_split(
            train_val,
            test_size=rel_val,
            random_state=42,
            stratify=train_val[target],
        )
    else:
        # fallback bez targetu
        train_val, test = train_test_split(df, test_size=0.15, random_state=42)
        rel_val = 0.15 / (1.0 - 0.15)
        train, val = train_test_split(train_val, test_size=rel_val, random_state=42)

    return train, val, test


# ----------------- Walidacje ----------------- #


def validate_clean(df: pd.DataFrame, params: dict | None = None) -> dict:
    """Sprawdzenie, czy dane po cleaningu są OK."""
    p = params or {}
    target = p.get("target")

    report = {
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "na_total": int(df.isna().sum().sum()),
        "na_by_col": df.isna().sum().to_dict(),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
    }

    # 1) brak braków
    if report["na_total"] > 0:
        raise ValueError(
            f"[validate_clean] Wykryto NaN po cleaningu: {report['na_total']}"
        )

    # 2) stałe kolumny (ignorujemy target)
    nunique = df.nunique(dropna=True)
    constant_cols = nunique[nunique <= 1].index.tolist()
    if target in constant_cols:
        constant_cols.remove(target)
    report["constant_cols"] = constant_cols
    if constant_cols:
        raise ValueError(
            f"[validate_clean] Kolumny stałe po cleaningu: {constant_cols}"
        )

    # 3) sanity-check: wiek, jeśli istnieje
    if "person_age" in df.columns:
        # czy wiek jest całkowity?
        if not np.allclose(df["person_age"], df["person_age"].round()):
            raise ValueError(
                "[validate_clean] person_age nie jest calkowity po cleaningu"
            )

        age_min = float(df["person_age"].min())
        age_max = float(df["person_age"].max())
        report["person_age_min"] = age_min
        report["person_age_max"] = age_max
        if age_min < 18 or age_max > 100:
            raise ValueError(
                f"[validate_clean] person_age poza zakresem [18, 100]: "
                f"min={age_min}, max={age_max}"
            )

    # 4) sanity-check: biny, jeśli istnieją
    if "person_age_bin" in df.columns:
        if df["person_age_bin"].isna().any():
            raise ValueError(
                "[validate_clean] person_age_bin zawiera NaN – problem z binningiem wieku."
            )

    if "person_income_bin" in df.columns:
        if df["person_income_bin"].isna().any():
            raise ValueError(
                "[validate_clean] person_income_bin zawiera NaN – problem z binningiem dochodu."
            )

    return report


def validate_scaled(df: pd.DataFrame, params: dict | None = None) -> dict:
    """
    Sprawdza, czy skalowane kolumny mają mean ~ 0 i std ~ 1.
    Kolumny wyłączone (target, id) są raportowane osobno.
    """
    p = params or {}
    target = p.get("target")
    id_col = p.get("id_col", "_row_id")

    tol_cfg = (p.get("validate", {}) or {}).get("scaled", {}) or {}
    tol_mean = float(tol_cfg.get("tol_mean", 1e-6))
    tol_std = float(tol_cfg.get("tol_std", 1e-3))

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in (target, id_col):
        if col in num_cols:
            num_cols.remove(col)

    means = {c: float(df[c].mean()) for c in num_cols}
    stds = {c: float(df[c].std(ddof=0)) for c in num_cols}
    bad_mean = [c for c in num_cols if abs(means[c]) > tol_mean]
    bad_std = [c for c in num_cols if abs(stds[c] - 1.0) > tol_std]

    report = {
        "num_cols": num_cols,
        "mean": means,
        "std": stds,
        "bad_mean_cols": bad_mean,
        "bad_std_cols": bad_std,
        "tol_mean": tol_mean,
        "tol_std": tol_std,
        "excluded": [c for c in [target, id_col] if c],
    }

    if bad_mean:
        raise ValueError(f"[validate_scaled] Srednia != 0 dla: {bad_mean[:5]} (...)")
    if bad_std:
        raise ValueError(f"[validate_scaled] Std != 1 dla: {bad_std[:5]} (...)")

    return report


def validate_split(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    params: dict | None = None,
) -> dict:
    """
    Walidacja:
    - proporcje train/val/test vs oczekiwane
    - brak przecieków między zbiorami (po _row_id lub po indeksach)
    """
    p = params or {}
    id_col = p.get("id_col", "_row_id")

    split_cfg = ((p.get("validate", {}) or {}).get("split", {}) or {})
    expected = split_cfg.get("expected", (0.70, 0.15, 0.15))
    expected = tuple(float(x) for x in expected)
    tol = float(split_cfg.get("tol", 0.03))

    n = len(train) + len(val) + len(test)
    ratios = (len(train) / n, len(val) / n, len(test) / n)
    delta = [abs(r - e) for r, e in zip(ratios, expected)]
    ok_ratios = all(d <= tol for d in delta)

    # overlap po stabilnym ID (fallback: index)
    if id_col in train.columns and id_col in val.columns and id_col in test.columns:
        set_tr = set(train[id_col].tolist())
        set_va = set(val[id_col].tolist())
        set_te = set(test[id_col].tolist())
        no_overlap_by = id_col
    else:
        set_tr, set_va, set_te = set(train.index), set(val.index), set(test.index)
        no_overlap_by = "index"

    no_leak = (
        set_tr.isdisjoint(set_va)
        and set_tr.isdisjoint(set_te)
        and set_va.isdisjoint(set_te)
    )

    report = {
        "n_total": int(n),
        "sizes": {
            "train": int(len(train)),
            "val": int(len(val)),
            "test": int(len(test)),
        },
        "ratios": {
            "train": ratios[0],
            "val": ratios[1],
            "test": ratios[2],
        },
        "expected": {
            "train": expected[0],
            "val": expected[1],
            "test": expected[2],
        },
        "ratios_within_tol": ok_ratios,
        "tolerance": tol,
        "no_overlap_by": no_overlap_by,
        "no_index_overlap": no_leak,
    }

    if not ok_ratios:
        raise ValueError(
            f"[validate_split] Zle proporcje: {report['ratios']} != {report['expected']} (+/-{tol})"
        )
    if not no_leak:
        raise ValueError(
            "[validate_split] Wykryto przecieki - nakladajace sie ID/indeksy miedzy zbiorami."
        )

    return report


# ----------------- Raport preprocessing ----------------- #


def _num_cols_excluding(df: pd.DataFrame, exclude: list[str]) -> list[str]:
    cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for c in exclude:
        if c in cols:
            cols.remove(c)
    return cols


def _fmt_value(v: float, as_int: bool = False) -> str:
    """Ładne formatowanie liczb do raportu:
    - int: bez przecinka
    - float: do 2 miejsc, bez zbędnych zer
    """
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "NaN"
    if as_int:
        return str(int(round(v)))
    s = f"{float(v):.2f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def build_preprocessing_report(
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    scaled_df: pd.DataFrame,
    clean_rep: dict,
    scaled_rep: dict,
    split_rep: dict,
    params: dict | None = None,
) -> str:
    """
    Buduje markdownowy raport preprocessingowy z porownaniem PRZED/PO:
    - braki danych
    - statystyki numeryczne (osobno dla PRZED i PO)
    - informacje o skalowaniu
    - informacje o podziale train/val/test
    - rozkłady nowych cech binningowych
    """
    p = params or {}
    target = p.get("target")
    id_col = p.get("id_col", "_row_id")

    tol_mean = scaled_rep.get("tol_mean", 1e-6)
    tol_std = scaled_rep.get("tol_std", 1e-3)
    excluded = scaled_rep.get("excluded", [])

    num_cols_scaled = scaled_rep.get("num_cols", [])
    excluded_cols = [c for c in [target, id_col] if c]
    num_cols_all = _num_cols_excluding(clean_df, excluded_cols)

    # kolumny, które raportujemy jako "intowe"
    int_like_cols = {
        "person_age",
        "person_emp_length",
        "cb_person_cred_hist_length",
        "loan_amnt",
        "person_income",
    }

    # braki przed/po
    na_before = raw_df.isna().sum().to_dict()
    na_after = clean_df.isna().sum().to_dict()

    # statystyki dla numerycznych (przed i po)
    def stats(df: pd.DataFrame, cols: list[str]) -> dict:
        desc = {}
        for c in cols:
            s = df[c].astype(float)
            desc[c] = {
                "min": float(np.nanmin(s)),
                "p25": float(np.nanpercentile(s, 25)),
                "median": float(np.nanmedian(s)),
                "p75": float(np.nanpercentile(s, 75)),
                "max": float(np.nanmax(s)),
                "mean": float(np.nanmean(s)),
                "std": float(np.nanstd(s)),
            }
        return desc

    cols_for_table = num_cols_all
    raw_stats = stats(raw_df, cols_for_table)
    clean_stats = stats(clean_df, cols_for_table)

    # informacje o skalowaniu
    means = scaled_rep.get("mean", {})
    stds = scaled_rep.get("std", {})
    badm = scaled_rep.get("bad_mean_cols", [])
    bads = scaled_rep.get("bad_std_cols", [])

    # split
    sizes = split_rep.get("sizes", {})
    ratios = split_rep.get("ratios", {})
    exp = split_rep.get("expected", {})
    no_overlap_by = split_rep.get("no_overlap_by", id_col)

    # budowa markdown
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    md: list[str] = []
    md.append("# Preprocessing report")
    md.append("")
    md.append(f"_Generated: {now}_")
    md.append("")

    # 1) Cleaning
    md.append("## 1) Cleaning - braki i zmiany")
    md.append(
        f"- Wiersze / kolumny po cleaningu: {clean_rep.get('rows', '?')} / {clean_rep.get('cols', '?')}"
    )
    md.append(
        f"- Braki lacznie po cleaningu: {clean_rep.get('na_total', '?')} (dokladny rozklad w tabeli nizej)"
    )
    md.append("")
    md.append("### 1.1 Braki danych - przed vs. po (TOP 10 wedlug liczby brakow przed)")
    md.append("| Kolumna | NaN (przed) | NaN (po) | roznica |")
    md.append("|---|---:|---:|---:|")
    na_pairs = sorted(na_before.items(), key=lambda x: x[1], reverse=True)[:10]
    for col, nb in na_pairs:
        na_b = int(nb)
        na_a = int(na_after.get(col, 0))
        md.append(f"| `{col}` | {na_b} | {na_a} | {na_a - na_b} |")
    md.append("")

    # 1.2 Statystyki PRZED
    md.append("### 1.2 Statystyki numeryczne PRZED czyszczeniem")
    md.append("| Kolumna | min | p25 | median | p75 | max | mean | std |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for c in cols_for_table:
        r = raw_stats[c]
        as_int = c in int_like_cols
        md.append(
            "| `{c}` | {vmin} | {vp25} | {vmed} | {vp75} | {vmax} | {vmean} | {vstd} |".format(
                c=c,
                vmin=_fmt_value(r["min"], as_int),
                vp25=_fmt_value(r["p25"], as_int),
                vmed=_fmt_value(r["median"], as_int),
                vp75=_fmt_value(r["p75"], as_int),
                vmax=_fmt_value(r["max"], as_int),
                vmean=_fmt_value(r["mean"], False),
                vstd=_fmt_value(r["std"], False),
            )
        )
    md.append("")

    # 1.3 Statystyki PO
    md.append("### 1.3 Statystyki numeryczne PO czyszczeniu")
    md.append("| Kolumna | min | p25 | median | p75 | max | mean | std |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for c in cols_for_table:
        k = clean_stats[c]
        as_int = c in int_like_cols
        md.append(
            "| `{c}` | {vmin} | {vp25} | {vmed} | {vp75} | {vmax} | {vmean} | {vstd} |".format(
                c=c,
                vmin=_fmt_value(k["min"], as_int),
                vp25=_fmt_value(k["p25"], as_int),
                vmed=_fmt_value(k["median"], as_int),
                vp75=_fmt_value(k["p75"], as_int),
                vmax=_fmt_value(k["max"], as_int),
                vmean=_fmt_value(k["mean"], False),
                vstd=_fmt_value(k["std"], False),
            )
        )
    md.append("")

    # 1.4 Podsumowanie zmian jakościowych
    md.append("#### 1.4 Podsumowanie zmian w rozkladach")
    md.append(
        "- Wiek (`person_age`): usunieto nielogiczne wartosci skrajne (np. 144 lat), "
        "rozklad srodka (median/mean) pozostaje praktycznie bez zmian."
    )
    md.append(
        "- Dochod (`person_income`): ucinamy najbardziej skrajne dochody (milionowe wartosci), "
        "dzieki czemu max i odchylenie standardowe spadaja, a median/mean zmieniaja sie niewiele."
    )
    md.append(
        "- Dlugosc zatrudnienia (`person_emp_length`): wartosci typu 123 lata sa traktowane jako outliery "
        "i przycinane do 99. percentyla (ok. kilkanascie lat); wiekszosc obserwacji z przedzialu 0–15 pozostaje bez zmian."
    )
    md.append(
        "- Kwota kredytu, oprocentowanie i wskazniki kredytowe (`loan_amnt`, `loan_int_rate`, "
        "`loan_percent_income`, `cb_person_cred_hist_length`): przyciete sa jedynie skrajne ogony, "
        "co redukuje wplyw pojedynczych ekstremalnych wartosci na model."
    )
    md.append("")

    # 1.5 Nowe cechy binningowe
    md.append("### 1.5 Nowe cechy binningowe (rozklad kategorii)")
    if "person_age_bin" in clean_df.columns:
        md.append("#### person_age_bin")
        vc = clean_df["person_age_bin"].value_counts(dropna=False).to_dict()
        for k, v in vc.items():
            md.append(f"- `{k}`: {v} obserwacji")
        md.append("")
    if "person_income_bin" in clean_df.columns:
        md.append("#### person_income_bin")
        vc = clean_df["person_income_bin"].value_counts(dropna=False).to_dict()
        for k, v in vc.items():
            md.append(f"- `{k}`: {v} obserwacji")
        md.append("")

    # 2) Scaling
    md.append("## 2) Scaling (StandardScaler)")
    md.append(f"- Skalowane kolumny numeryczne: {len(num_cols_scaled)}")
    if num_cols_scaled:
        md.append("  - " + ", ".join(f"`{c}`" for c in num_cols_scaled))
    if excluded:
        md.append(
            "- Kolumny wylaczone ze skalowania: "
            + ", ".join(f"`{c}`" for c in excluded)
        )
    md.append(f"- Tolerancje: mean={tol_mean}, std={tol_std}")
    if badm or bads:
        md.append(f"- Uwaga: mean != 0 dla: {badm}, std != 1 dla: {bads}")
    else:
        md.append(
            "- Wszystkie skalowane kolumny mieszcza sie w tolerancjach "
            "(mean okolo 0, std okolo 1)."
        )
    md.append("")

    # 3) Split
    md.append("## 3) Split - train / val / test")
    md.append(
        f"- Rozmiary: train {sizes.get('train')}, val {sizes.get('val')}, "
        f"test {sizes.get('test')} (total {split_rep.get('n_total')})"
    )
    md.append(
        f"- Udzialy: train {ratios.get('train'):.3f}, val {ratios.get('val'):.3f}, "
        f"test {ratios.get('test'):.3f} | oczekiwane: {exp}"
    )
    md.append(
        f"- Brak przeciekow (overlap po `{no_overlap_by}`): "
        f"{split_rep.get('no_index_overlap', False)}"
    )
    md.append("")

    # 4) Decyzje
    md.append("---")
    md.append("## 4) Decyzje i uwagi")
    md.append("- Missing values: num = median, cat = most_frequent.")
    md.append(
        "- Outliery: domenowe przyciecia/usuwanie na kluczowych kolumnach na podstawie EDA "
        "(wiek, dochod, emp_length, historia kredytowa, loan_percent_income) "
        "plus ogolny clipping IQR dla pozostalych numerycznych."
    )
    md.append(
        "- Nowe cechy: binning wieku (`person_age_bin`) i dochodu (`person_income_bin`) "
        "dla lepszej pracy modeli liniowych i interpretowalnosci."
    )
    md.append(
        "- Scaling: StandardScaler na kolumnach numerycznych (bez targetu i ID)."
    )
    md.append(
        "- Split: 70 / 15 / 15, random_state=42, kontrola overlapu po stabilnym ID."
    )
    md.append("")

    return "\n".join(md)
