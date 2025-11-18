# Raport EDA

- Wiersze: **32581**, Kolumny: **12**

- Kolumny numeryczne (8): person_age, person_income, person_emp_length, loan_amnt, loan_int_rate, loan_status, loan_percent_income, cb_person_cred_hist_length
- Kolumny kategoryczne (4): person_home_ownership, loan_intent, loan_grade, cb_person_default_on_file

## Braki danych
Zobacz wykres: `docs/eda/missingness.png`

## Korelacje (numeryczne)
Mapa korelacji: `docs/eda/correlation_heatmap.png`

## Rozkłady zmiennych numerycznych
Folder: `docs/eda/numeric`

## Rozkłady zmiennych kategorycznych
Folder: `docs/eda/categorical`

## Wskazówki do dalszych kroków
- Uzupełnienie/obsługa braków danych (medianą/modą lub imputacją wielowymiarową).
- Standaryzacja/normalizacja kolumn numerycznych.
- Enkodowanie zmiennych kategorycznych (One-Hot/Target Encoding).
- Usunięcie lub transformacja outlierów (np. winsoryzacja).
