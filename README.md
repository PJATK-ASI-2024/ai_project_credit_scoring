# 💳 AI Credit Scoring

## 🎯 Cel projektu

Celem projektu jest stworzenie systemu do **oceny ryzyka kredytowego (credit scoring)** z wykorzystaniem danych historycznych o klientach.  
Model analizuje cechy takie jak wiek, dochód, długość zatrudnienia czy historia kredytowa, aby przewidzieć, czy klient jest **niskiego** czy **wysokiego ryzyka** kredytowego.

Projekt prezentuje kompletny proces **ETL → Feature Engineering → Modelowanie → Raportowanie**, zrealizowany w architekturze **Kedro Pipeline**.

Dane pochodzą z:  
🔗 **Credit Risk Dataset – Kaggle**  
https://www.kaggle.com/datasets/laotse/credit-risk-dataset

---

# 📦 1. Zakres projektu

## 🔧 ETL i przetwarzanie danych (Kedro)
- ładowanie danych surowych  
- czyszczenie i imputacja  
- walidacja jakości  
- generowanie raportu preprocessingowego  

## 🔎 Analiza eksploracyjna (EDA)
- brakujące wartości  
- korelacje  
- rozkłady zmiennych  
- raport EDA (`docs/eda/eda_report.md`)

## 🤖 Modelowanie (Moduł ML)
Zaimplementowano pełny pipeline modelowania:

### 1️⃣ Baseline – DummyClassifier  
- model odniesienia  
- zapis metryk: `baseline_metrics.json`

### 2️⃣ AutoML-light (sklearn)  
Automatyczne porównanie trzech modeli:
- Logistic Regression  
- RandomForest  
- GradientBoosting  

Wyniki:
- `automl_metrics.json`  
- `automl_model.pkl`  
- `automl_results.csv`  
- wybór najlepszego modelu po F1-score

### 3️⃣ Custom RandomForest  
- ręcznie strojoną konfiguracja  
- zapis metryk: `custom_metrics.json`

### 4️⃣ Porównanie modeli  
- wybór najlepszego modelu (`model_comparison.json`)

### 5️⃣ Raport końcowy modelowania  
- `docs/modeling_report.md`


---

# 🧰 3. Technologie

- **Python 3.12**
- **Kedro 0.19+**
- **Apache Airflow 2.9.0**
- **pandas / numpy**
- **scikit-learn**
- **matplotlib**
- **Jupyter Notebook**
- **Git / GitHub**
- **Docker / Docker Compose**

---

# ⚙️ 4. Pipeline przetwarzania danych

## 1️⃣ Czyszczenie danych (`clean_data`)
- konwersje typów  
- imputacja braków  
- sanity-checki  
- clipping IQR  
- binning wieku i dochodu  
- dodanie `_row_id`  

## 2️⃣ Skalowanie (`scale_data`)
- StandardScaler dla zmiennych numerycznych

## 3️⃣ Podział danych (`split_data`)
- train / validation / test  
- podział stratified  

## 4️⃣ Walidacje
- `validate_clean`  
- `validate_scaled`  
- `validate_split`  

## 5️⃣ Raport preprocessingowy
- generowany automatycznie:  
  `docs/preprocessing_report.md`

---

# 🤖 5. Pipeline modelowania ML

Pipeline modelowania zawiera:

```
baseline → automl → custom → evaluate
```

### Wyniki zapisują się do:

```
data/08_reporting/
├── baseline_metrics.json
├── automl_metrics.json
├── automl_model.pkl
├── automl_results.csv
├── custom_metrics.json
└── model_comparison.json
```

---

# 📈 6. Wizualizacje

Znajdują się w `docs/plots/`:

- **metrics_comparison.png** – porównanie metryk modeli  
- **feature_importance.png** – ważność cech dla RandomForest  

---

# 📄 7. Raport końcowy

Pełny raport modelowania:  
➡ **docs/modeling_report.md**

Zawiera:
- metryki modeli  
- porównanie jakości  
- wykresy  
- rekomendacje  

---

# 🔄 8. Orkiestracja z Apache Airflow

Projekt wykorzystuje **Apache Airflow** do automatyzacji i orkiestracji pipeline'ów Kedro.

## DAG: `kedro_project_pipeline`

Przepływ zadań:
```
eda → preprocessing → modeling → evaluation
```

### Uruchomienie Airflow

1. **Uruchom Docker Desktop**
2. **Wystartuj Airflow:**
   ```bash
   cd e:\Projekty\ASI\ai-credit-scoring
   docker-compose up -d
   ```
3. **Otwórz interfejs:**
   - URL: http://localhost:8080
   - Login: `admin` / `admin`

### Dokumentacja

- 📋 [AIRFLOW_SETUP.md](docs/AIRFLOW_SETUP.md) - Instrukcje krok po kroku
- 📊 [airflow_report.md](docs/airflow_report.md) - Szczegółowy raport
- 🎨 Screenshots: `docs/screenshots/`

### Funkcjonalności

✅ Automatyczne harmonogramowanie  
✅ Monitoring wykonania pipeline'ów  
✅ Retry przy błędach  
✅ Historia wykonań i logów  
✅ Integracja z Kedro  

---

# 👥 9. Autor

| Imię i nazwisko | Rola |
|----------------|-------|
| **Maciej Wojdowski** | Data Scientist / ML Engineer |

---

# 🏁 Status projektu

Projekt zawiera kompletny pipeline:
- EDA  
- preprocessing  
- modelowanie  
- raportowanie
- **orkiestracja z Airflow** 🆕

