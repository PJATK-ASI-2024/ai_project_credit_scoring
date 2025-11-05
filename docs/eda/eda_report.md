🧩 Raport EDA — Credit Risk Dataset

## 📘 Opis danych

Zbiór `credit_risk_dataset.csv` zawiera **32 581 rekordów** oraz **12 kolumn** opisujących dane klientów ubiegających się o kredyt.

**Zmienna docelowa:** `loan_status`  
- `0` – kredyt spłacony  
- `1` – kredyt niespłacony  

### Typy kolumn:
- **Numeryczne:** `person_age`, `person_income`, `person_emp_length`, `loan_amnt`, `loan_int_rate`, `loan_percent_income`, `cb_person_cred_hist_length`
- **Kategoryczne:** `person_home_ownership`, `loan_intent`, `loan_grade`, `cb_person_default_on_file`
- **Docelowa:** `loan_status`

---

## 📊 Analiza statystyczna

| Zmienna | Średnia | Odch. std | Min | 25% | 50% | 75% | Max |
|----------|----------|------------|-----|-----|-----|-----|-----|
| person_age | 27.7 | 6.35 | 20 | 23 | 26 | 30 | 144 |
| person_income | 66 074 | 61 983 | 4 000 | 38 500 | 55 000 | 79 200 | 6 000 000 |
| person_emp_length | 4.79 | 4.14 | 0 | 2 | 4 | 7 | 123 |
| loan_amnt | — | — | 500 | 5 000 | 8 000 | 12 200 | 35 000 |
| loan_int_rate | — | — | — | — | — | — | — |
| loan_percent_income | — | — | — | — | — | — | — |

**Obserwacje:**
- Średni wiek: **27.7 lat**, większość klientów w przedziale 23–30 lat.  
- Dochód jest bardzo zróżnicowany — od **4 000 do 6 000 000**, mediana: **66 000**.   
- Długość zatrudnienia (`person_emp_length`) – średnio 4.8 roku, ale z dużym rozrzutem.  
- Kwoty pożyczek (`loan_amnt`) – mediana 8 000, maks. 35 000, co sugeruje głównie mikropożyczki.

---

## 🧮 Braki danych

| Kolumna | Liczba braków | Udział % |
|----------|---------------|-----------|
| loan_int_rate | 3 116 | 9.56% |
| person_emp_length | 895 | 2.75% |
| pozostałe kolumny | 0 | 0.00% |

🧩 **Wnioski:**
- Braki występują głównie w `loan_int_rate` i `person_emp_length`.  
- Warto uzupełnić:
  - `loan_int_rate` — medianą lub imputacją regresyjną na podstawie `loan_amnt` i `loan_grade`,
  - `person_emp_length` — medianą w grupie o podobnym `person_income`.

---

## 🔗 Korelacje

| Zmienna 1 | Zmienna 2 | Korelacja (r) | Wniosek |
|------------|------------|----------------|----------|
| person_age | cb_person_cred_hist_length | **0.86** | Dłuższa historia kredytowa u starszych klientów. |
| person_income | loan_amnt | 0.27 | Wyższe dochody → wyższe kwoty kredytów. |
| loan_percent_income | person_income | -0.25 | Im większy dochód, tym mniejszy procent dochodu stanowi kredyt. |
| person_emp_length | person_age | 0.16 | Naturalna zależność wieku i długości pracy. |
| loan_status | person_income | -0.14 | Niższy dochód → większe ryzyko niespłaty. |

📈 Brak silnych współliniowości między predyktorami (|r| > 0.9).

---

## 🎯 Analiza zmiennej docelowej — `loan_status`

| Klasa | Liczba | Udział % |
|--------|---------|-----------|
| 0 – spłacony | 25 473 | **78.2%** |
| 1 – niespłacony | 7 108 | **21.8%** |

⚠️ Dane są **niezbalansowane** — zdecydowanie więcej kredytów spłaconych.

### Zależności z innymi zmiennymi:
| Cecha | Wniosek |
|--------|----------|
| `person_income` | Kredytobiorcy z niższym dochodem (< 30 000) częściej nie spłacają pożyczek. |
| `loan_intent` | Największy udział niespłat w pożyczkach „DEBTCONSOLIDATION” i „MEDICAL”. |
| `loan_grade` | Ryzyko wzrasta od A → E; klienci z klasą A spłacają znacznie częściej. |
| `cb_person_default_on_file` | Osoby z historią „Y” mają większy odsetek niespłat. |

---

## ⚠️ Wartości odstające

| Zmienna | Liczba outlierów |
|----------|------------------|
| person_age | 1 494 |
| person_income | 1 484 |
| person_emp_length | 853 |
| loan_amnt | 1 689 |
| loan_int_rate | 6 |
| loan_percent_income | 651 |
| cb_person_cred_hist_length | 1 142 |

**Komentarz:**
- Wiek powyżej 100 lat i dochody > 200 000 to outliery.  
- `loan_amnt` ma kilka wartości powyżej 30 000 (górny 1%).  
- Zalecana **winsoryzacja (99. percentyl)** lub **log-transformacja dochodu**.

---

## 🏠 Zmienne kategoryczne

| Zmienna | Najczęstsze wartości (udział %) |
|----------|---------------------------------|
| `person_home_ownership` | RENT (50%), MORTGAGE (41%), OWN (8%) |
| `loan_intent` | EDUCATION (20%), MEDICAL (19%), VENTURE (18%), PERSONAL (17%), DEBTCONSOLIDATION (16%) |
| `loan_grade` | A (33%), B (32%), C (20%), D (11%), E (3%) |
| `cb_person_default_on_file` | N (82%), Y (18%) |

💡 **Wniosek:**  
Większość klientów wynajmuje mieszkania i zaciąga kredyty na edukację, medycynę lub biznes.

---

## 📈 Percentyle (wybrane zmienne)

| Zmienna | 25% | 50% | 75% | 90% | 99% | Max |
|----------|-----|-----|-----|-----|-----|-----|
| person_income | 38 500 | 55 000 | 79 200 | 110 000 | 225 200 | 6 000 000 |
| loan_amnt | 5 000 | 8 000 | 12 200 | 19 000 | 29 800 | 35 000 |

📊 Dochody powyżej 225 000 i kredyty powyżej 30 000 można uznać za **ekstremalne wartości**.

---

## 🧠 Wnioski biznesowe

- **Dochód** i **oprocentowanie kredytu** mają największy wpływ na ryzyko niespłaty.  
- Klienci z historią kredytową (`cb_person_default_on_file = Y`) częściej nie spłacają kredytów.  
- Dane wymagają dalszej **standaryzacji** i **zbalansowania klas** (`SMOTE` lub wagowanie).  
- Duże rozbieżności w `person_income` sugerują potrzebę logarytmizacji lub standaryzacji.

---

## ⚙️ Rekomendacje dla preprocessing

1. Uzupełnić:
   - `loan_int_rate` medianą lub modelem regresyjnym,
   - `person_emp_length` medianą w grupach wg `person_income`.
2. Przeskalować zmienne numeryczne (`StandardScaler` lub `RobustScaler`).  
3. Zastosować **One-Hot Encoding** dla zmiennych kategorycznych (`loan_grade`, `loan_intent`, `person_home_ownership`).  
4. Ograniczyć outliery do 99. percentyla.  
5. Rozważyć **balansowanie klas** w `loan_status` (SMOTE, class weights).

---

📅 **Podsumowanie:**  
Analiza ujawnia wyraźne różnice między klientami spłacającymi i niespłacającymi kredyty — dochód, długość zatrudnienia i cel pożyczki to kluczowe predyktory.  
Zbiór wymaga czyszczenia i standaryzacji przed modelowaniem.
"""

