# 💳 AI Credit Scoring

## 🎯 Cel projektu

Celem projektu jest stworzenie systemu do **oceny ryzyka kredytowego (credit scoring)** z wykorzystaniem danych historycznych o klientach.  
Model analizuje cechy takie jak wiek, dochód, długość zatrudnienia czy historia kredytowa, aby przewidzieć, czy klient jest **niskiego** czy **wysokiego ryzyka** kredytowego.

Projekt ma charakter edukacyjny i prezentuje kompletny proces **ETL → Feature Engineering → Raportowanie** w architekturze opartej o **Kedro**.

Dane pochodzą z:  
🔗 **Credit Risk Dataset – Kaggle**  
https://www.kaggle.com/datasets/laotse/credit-risk-dataset

---

# 📦 Zakres projektu

🔧 **ETL i przetwarzanie danych (Kedro)**  
- ładowanie danych surowych  
- kompleksowe czyszczenie  
- imputacja braków  
- walidacja pipeline’u  
- generowanie raportu preprocessingowego (markdown)  

🧠 **Feature Engineering**  
- binning wieku (`person_age_bin`)  
- binning dochodu (`person_income_bin`)  
- usuwanie i przycinanie outlierów  

📊 **Raportowanie**  
- raport preprocessingowy (`preprocessing_report.md`)  
- notebook EDA

---

# 🗂️ Struktura projektu

```
ai_credit_scoring/
├── conf/
│   ├── base/                         # Config: katalog, parametry pipeline’u
│   └── local/                        # Parametry lokalne (gitignore)
│
├── data/
│   ├── 01_raw/                       # Dane surowe
│   ├── 02_intermediate/              # Dane po czyszczeniu
│   ├── 05_model_input/               # Train / val / test (po split)
│   └── 08_reporting/                 # Raporty (preprocessing, EDA)
│
├── docs/
│   ├── architecture_diagram.png      # Architektura systemu
│   ├── eda/eda_report.md             # Raport z EDA
│   └── preprocessing_report.md       # Raport z czyszczenia danych
│
├── notebooks/
│   └── EDA_credit_scoring.ipynb      # Analiza eksploracyjna
│
├── src/ai_credit_scoring/
│   ├── pipelines/
│   │   └── preprocessing/            # Czyszczenie i przygotowanie danych
│   ├── settings.py
│   └── __init__.py
│
│
├── README.md
└── requirements.txt
```

---

# 🧰 Technologie

- **Python 3.10+**
- **Kedro 0.19+**
- **pandas / numpy**
- **scikit-learn**
- **matplotlib / seaborn**
- **Git / GitHub**

---

# ⚙️ Pipeline przetwarzania danych

### 1️⃣ Czyszczenie danych (`clean_data`)
- konwersje typów  
- usuwanie kolumn/wierszy z dużą liczbą braków  
- imputacja medianą / most frequent  
- sanity-checki:  
  - wiek w zakresie **[18, 90]**  
  - przycinanie 99. percentyla dla dochodu i historii kredytowej  
- ogólny clipping IQR  
- wymuszenie wieku jako **liczby całkowitej**  
- binning:  
  - `person_age_bin` → 18–25, 26–35, 36–45, 46–60, 60+  
  - `person_income_bin` → kwantyle 0–20–40–60–80–95–100%  
- dodanie `_row_id` (kontrola przecieków)  

### 2️⃣ Skalowanie (`scale_data`)
- StandardScaler dla zmiennych numerycznych

### 3️⃣ Podział danych (`split_data`)
- train (70%)  
- validation (15%)  
- test (15%)  
- podział stratified (jeśli jest target)

### 4️⃣ Walidacje
- `validate_clean`  
- `validate_scaled`  
- `validate_split`  

### 5️⃣ Raport preprocessingowy
- generowany automatycznie: `docs/preprocessing_report.md`

---

# 🧪 Testy jednostkowe

Plik: `tests/test_nodes.py`

Testy obejmują:

- poprawność czyszczenia  
- poprawność wieku i binów  
- sprawdzenie skalowania  
- stratified split  
- walidacje pozytywne i negatywne  

--- 

# 👥 Autor

| Imię i nazwisko | Rola | GitHub |
|------------------|---------------------------|---------|
| **Maciej Wojdowski** | Data Scientist / ML Engineer | maciejwoj |

---

# 🔗 Linki

- Repozytorium:  
  https://github.com/PJATK-ASI-2024/ai_project_credit_scoring

- Tablica zadań (GitHub Projects):  
  https://github.com/orgs/PJATK-ASI-2024/projects

- Raport EDA:  
  `docs/eda/eda_report.md`

- Raport preprocessingowy:  
  `docs/preprocessing_report.md`


---

# 🏁 Status
Projekt zawiera kompletny pipeline do czyszczenia danych wraz z raportowaniem i testami.  
Etap modelowania ML zostanie dodany później.

