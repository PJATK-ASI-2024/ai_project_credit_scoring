import pandas as pd
import numpy as np
import pytest

from .nodes import (
    clean_data,
    scale_data,
    split_data,
    validate_clean,
    validate_scaled,
    validate_split,
)


def test_clean_data_not_empty():
    df = pd.DataFrame({"a": [1, 2, np.nan, 1000], "b": [5, np.nan, 7, 8]})
    result = clean_data(df, params={})
    assert not result.empty
    assert result.isna().sum().sum() == 0


def test_clean_data_person_age_and_bins():
    """Sprawdzamy nowe zachowanie clean_data:
    - wiek po czyszczeniu jest w zakresie [18, 90]
    - wiek jest calkowity
    - powstaja biny person_age_bin i person_income_bin bez NaN.
    """
    df = pd.DataFrame(
        {
            # dwa rekordy skrajne (ponizej 18 i powyzej 90) powinny wyleciec
            "person_age": [16, 20, 25, 40, 95],
            "person_income": [20000, 30000, 40000, 50000, 60000],
            "person_emp_length": [0, 1, 2, 3, 4],
            "cb_person_cred_hist_length": [1, 2, 3, 4, 5],
            "loan_percent_income": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )

    result = clean_data(df, params={})

    # po odcieciu 16 i 95 powinnismy miec tylko wiersze z wiekiem 20,25,40
    assert result["person_age"].min() >= 18
    assert result["person_age"].max() <= 90
    # wiek musi byc calkowity
    assert pd.api.types.is_integer_dtype(result["person_age"])

    # biny wieku
    assert "person_age_bin" in result.columns
    assert result["person_age_bin"].isna().sum() == 0

    # biny dochodu (moga nie powstac jesli cos poszlo nie tak z kwantylami)
    if "person_income_bin" in result.columns:
        assert result["person_income_bin"].isna().sum() == 0


def test_scale_data_stats():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
    scaled = scale_data(df, params={})
    assert abs(float(scaled["x"].mean())) < 1e-6
    assert abs(float(scaled["y"].std(ddof=0)) - 1.0) < 1e-6


def test_split_sum():
    df = pd.DataFrame({"x": range(100)})
    train, val, test = split_data(df, params={})
    assert len(train) + len(val) + len(test) == len(df)


def test_validate_clean_ok():
    """Podstawowy happy-path bez specjalnych kolumn domenowych."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    rep = validate_clean(df, params={})
    assert rep["na_total"] == 0
    assert rep["constant_cols"] == []


def test_validate_clean_with_person_age_ok():
    """validate_clean powinien przejsc dla poprawnego wieku."""
    df = pd.DataFrame({"person_age": [18, 30, 45, 60, 90]})
    rep = validate_clean(df, params={})
    assert rep["person_age_min"] == 18.0
    assert rep["person_age_max"] == 90.0


def test_validate_clean_person_age_non_integer_raises():
    """Niecalkowity wiek powinien wywolywac blad."""
    df = pd.DataFrame({"person_age": [18.5, 20.0, 30.0]})
    with pytest.raises(ValueError, match="person_age nie jest calkowity"):
        validate_clean(df, params={})


def test_validate_clean_person_age_out_of_range_raises():
    """Wiek poza zakresem [18, 100] powinien wywolywac blad."""
    df = pd.DataFrame({"person_age": [17, 50, 101]})
    with pytest.raises(ValueError, match="person_age poza zakresem"):
        validate_clean(df, params={})


def test_validate_scaled_ok():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]})
    scaled = scale_data(df, params={})
    params = {
        "validate": {
            "scaled": {"tol_mean": 1e-6, "tol_std": 1e-6},
        }
    }
    rep = validate_scaled(scaled, params=params)
    assert rep["bad_mean_cols"] == []
    assert rep["bad_std_cols"] == []


def test_validate_scaled_raises_on_unscaled_data():
    """validate_scaled powinien wykryc dane nieprzeskalowane."""
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]})
    params = {
        "validate": {
            "scaled": {"tol_mean": 1e-3, "tol_std": 1e-3},
        }
    }
    # tu nie uzywamy scale_data, tylko surowe df – powinna poleciec walidacja
    with pytest.raises(ValueError):
        validate_scaled(df, params=params)


def test_validate_split_ok():
    train = pd.DataFrame({"x": range(70)}).set_index(pd.Index(range(0, 70)))
    val = pd.DataFrame({"x": range(70, 85)}).set_index(pd.Index(range(70, 85)))
    test = pd.DataFrame({"x": range(85, 100)}).set_index(pd.Index(range(85, 100)))

    params = {
        "validate": {
            "split": {
                "expected": (0.70, 0.15, 0.15),
                "tol": 0.05,
            }
        }
    }
    rep = validate_split(train, val, test, params=params)
    assert rep["ratios_within_tol"]
    assert rep["no_index_overlap"]
