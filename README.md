# 💳 AI Credit Scoring

## 🎯 Cel projektu
Celem projektu jest stworzenie systemu do **oceny ryzyka kredytowego (credit scoring)** z wykorzystaniem danych historycznych o klientach.  
Model analizuje cechy takie jak wiek, dochód, stan cywilny czy historia finansowa, aby przewidzieć, czy klient jest **niskiego** czy **wysokiego ryzyka** kredytowego.

Projekt ma charakter edukacyjny i może zostać wykorzystany jako przykład wdrożenia kompletnego pipeline’u **ETL + Machine Learning** w środowisku produkcyjnym.

Dane pochodzą z: [Credit Risk Dataset – Kaggle](https://www.kaggle.com/datasets/laotse/credit-risk-dataset)

---

## 📦 Zakres projektu
- **ETL (Kedro)** – ładowanie, czyszczenie i przetwarzanie danych, zapis do `data/02_intermediate`.  
- **Feature Engineering** – tworzenie nowych cech na podstawie danych surowych.  
- **Model ML (scikit-learn)** – klasyfikacja klientów jako „dobrych” lub „złych” kredytowo (np. Logistic Regression, Random Forest, XGBoost).  
- **Ewaluacja modelu** – metryki: Accuracy, ROC AUC, Precision, Recall.  
- **Raport końcowy (Jupyter / EDA)** – wizualizacja wyników i ważności cech.  
- **Docker / CI (opcjonalnie)** – możliwość uruchomienia projektu w środowisku kontenerowym.  

---

## 🗂️ Struktura katalogów
````text
ai_credit_scoring/
├── conf/
│   ├── base/                      # Konfiguracja Kedro (catalog, parameters)
│   └── local/                     # Ustawienia lokalne
├── data/
│   ├── 01_raw/                    # Dane surowe
│   ├── 02_intermediate/           # Dane przetworzone
│   ├── 06_models/                 # Wytrenowane modele
│   └── 08_reporting/              # Raporty i wyniki
├── notebooks/                     # Analiza EDA i testy
├── src/ai_credit_scoring/         # Główny kod projektu
│   ├── pipelines/credit_scoring/  # Definicja pipeline’u ETL + ML
│   └── settings.py
├── requirements.txt
├── README.md
└── LICENSE
````

---

## 🧰 Technologie
- **Python 3.10+**
- **Kedro 1.0.0**
- **pandas, numpy, scikit-learn, matplotlib**
- **seaborn, xgboost**
- **Git / GitHub**

---




## 👥 Członek zespołu

| Imię i nazwisko | Rola w projekcie | GitHub login |
|------------------|------------------|--------------|
| **Maciej Wojdowski** | Data Scientist / ML Engineer | maciejwoj    |

---

## 🔗 Linki projektu
- Repozytorium GitHub: [https://github.com/PJATK-ASI-2024/ai_project_credit_scoring](https://github.com/PJATK-ASI-2024/ai_project_credit_scoring)
- Tablica zadań (GitHub Project): [https://github.com/orgs/PJATK-ASI-2024/projects](https://github.com/orgs/PJATK-ASI-2024/projects)
- Dokumentacja:  `docs/architecture_diagram.png`
- 📘 Notebook EDA: `notebooks/EDA_teamX.ipynb`
- 📄 Raport EDA: `docs/eda/eda_report.md`
---
