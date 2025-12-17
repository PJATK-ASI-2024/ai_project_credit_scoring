# Preprocessing report

_Generated: 2025-12-17 15:39:54_

## 1) Cleaning - braki i zmiany
- Wiersze / kolumny po cleaningu: 32575 / 15
- Braki lacznie po cleaningu: 0 (dokladny rozklad w tabeli nizej)

### 1.1 Braki danych - przed vs. po (TOP 10 wedlug liczby brakow przed)
| Kolumna | NaN (przed) | NaN (po) | roznica |
|---|---:|---:|---:|
| `loan_int_rate` | 3116 | 0 | -3116 |
| `person_emp_length` | 895 | 0 | -895 |
| `person_age` | 0 | 0 | 0 |
| `person_income` | 0 | 0 | 0 |
| `person_home_ownership` | 0 | 0 | 0 |
| `loan_intent` | 0 | 0 | 0 |
| `loan_grade` | 0 | 0 | 0 |
| `loan_amnt` | 0 | 0 | 0 |
| `loan_status` | 0 | 0 | 0 |
| `loan_percent_income` | 0 | 0 | 0 |

### 1.2 Statystyki numeryczne PRZED czyszczeniem
| Kolumna | min | p25 | median | p75 | max | mean | std |
|---|---:|---:|---:|---:|---:|---:|---:|
| `person_age` | 20 | 23 | 26 | 30 | 144 | 27.73 | 6.35 |
| `person_income` | 4000 | 38500 | 55000 | 79200 | 6000000 | 66074.85 | 61982.17 |
| `person_emp_length` | 0 | 2 | 4 | 7 | 123 | 4.79 | 4.14 |
| `loan_amnt` | 500 | 5000 | 8000 | 12200 | 35000 | 9589.37 | 6321.99 |
| `loan_int_rate` | 5.42 | 7.9 | 10.99 | 13.47 | 23.22 | 11.01 | 3.24 |
| `loan_percent_income` | 0 | 0.09 | 0.15 | 0.23 | 0.83 | 0.17 | 0.11 |
| `cb_person_cred_hist_length` | 2 | 3 | 4 | 8 | 30 | 5.8 | 4.05 |

### 1.3 Statystyki numeryczne PO czyszczeniu
| Kolumna | min | p25 | median | p75 | max | mean | std |
|---|---:|---:|---:|---:|---:|---:|---:|
| `person_age` | 20 | 23 | 26 | 30 | 84 | 27.72 | 6.19 |
| `person_income` | 4000 | 38500 | 55000 | 79200 | 140250 | 62412.21 | 31802.96 |
| `person_emp_length` | 0 | 2 | 4 | 7 | 14 | 4.68 | 3.72 |
| `loan_amnt` | 500 | 5000 | 8000 | 12200 | 23000 | 9407.49 | 5812.71 |
| `loan_int_rate` | 5.42 | 8.49 | 10.99 | 13.11 | 20.04 | 11.01 | 3.08 |
| `loan_percent_income` | 0 | 0.09 | 0.15 | 0.23 | 0.44 | 0.17 | 0.1 |
| `cb_person_cred_hist_length` | 2 | 3 | 4 | 8 | 16 | 5.71 | 3.71 |

#### 1.4 Podsumowanie zmian w rozkladach
- Wiek (`person_age`): usunieto nielogiczne wartosci skrajne (np. 144 lat), rozklad srodka (median/mean) pozostaje praktycznie bez zmian.
- Dochod (`person_income`): ucinamy najbardziej skrajne dochody (milionowe wartosci), dzieki czemu max i odchylenie standardowe spadaja, a median/mean zmieniaja sie niewiele.
- Dlugosc zatrudnienia (`person_emp_length`): wartosci typu 123 lata sa traktowane jako outliery i przycinane do 99. percentyla (ok. kilkanascie lat); wiekszosc obserwacji z przedzialu 0–15 pozostaje bez zmian.
- Kwota kredytu, oprocentowanie i wskazniki kredytowe (`loan_amnt`, `loan_int_rate`, `loan_percent_income`, `cb_person_cred_hist_length`): przyciete sa jedynie skrajne ogony, co redukuje wplyw pojedynczych ekstremalnych wartosci na model.

### 1.5 Nowe cechy binningowe (rozklad kategorii)
#### person_age_bin
- `18-25`: 15352 obserwacji
- `26-35`: 13763 obserwacji
- `36-45`: 2814 obserwacji
- `46-60`: 582 obserwacji
- `60+`: 64 obserwacji

#### person_income_bin
- `(3999.999, 35000.0]`: 6629 obserwacji
- `(35000.0, 49000.0]`: 6546 obserwacji
- `(63000.0, 86000.0]`: 6513 obserwacji
- `(49000.0, 63000.0]`: 6397 obserwacji
- `(86000.0, 138000.0]`: 4876 obserwacji
- `(138000.0, 140250.0]`: 1614 obserwacji

## 2) Scaling (StandardScaler)
- Skalowane kolumny numeryczne: 7
  - `person_age`, `person_income`, `person_emp_length`, `loan_amnt`, `loan_int_rate`, `loan_percent_income`, `cb_person_cred_hist_length`
- Kolumny wylaczone ze skalowania: `loan_status`, `_row_id`
- Tolerancje: mean=1e-06, std=0.001
- Wszystkie skalowane kolumny mieszcza sie w tolerancjach (mean okolo 0, std okolo 1).

## 3) Split - train / val / test
- Rozmiary: train 22801, val 4887, test 4887 (total 32575)
- Udzialy: train 0.700, val 0.150, test 0.150 | oczekiwane: {'train': 0.7, 'val': 0.15, 'test': 0.15}
- Brak przeciekow (overlap po `_row_id`): True

---
## 4) Decyzje i uwagi
- Missing values: num = median, cat = most_frequent.
- Outliery: domenowe przyciecia/usuwanie na kluczowych kolumnach na podstawie EDA (wiek, dochod, emp_length, historia kredytowa, loan_percent_income) plus ogolny clipping IQR dla pozostalych numerycznych.
- Nowe cechy: binning wieku (`person_age_bin`) i dochodu (`person_income_bin`) dla lepszej pracy modeli liniowych i interpretowalnosci.
- Scaling: StandardScaler na kolumnach numerycznych (bez targetu i ID).
- Split: 70 / 15 / 15, random_state=42, kontrola overlapu po stabilnym ID.
