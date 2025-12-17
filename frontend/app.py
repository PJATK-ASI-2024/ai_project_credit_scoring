"""
Credit Scoring Frontend - Streamlit App

Interfejs użytkownika do predykcji ryzyka kredytowego.
Komunikuje się z FastAPI backendem.
"""

import streamlit as st
import requests
import json

import os

# === Konfiguracja ===
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Render przekazuje sam hostname (bez https://) w property: host, więc musimy to obsłużyć
if not API_URL.startswith("http"):
    API_URL = f"https://{API_URL}"

# === Ustawienia strony ===
st.set_page_config(
    page_title="Credit Scoring - Ocena Ryzyka Kredytowego",
    page_icon="💳",
    layout="wide"
)

# === Styl CSS ===
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .low-risk {
        background-color: #C8E6C9;
        border: 2px solid #4CAF50;
    }
    .medium-risk {
        background-color: #FFF9C4;
        border: 2px solid #FFC107;
    }
    .high-risk {
        background-color: #FFCDD2;
        border: 2px solid #F44336;
    }
</style>
""", unsafe_allow_html=True)

# === Nagłówek ===
st.markdown('<p class="main-header">💳 Ocena Ryzyka Kredytowego</p>', unsafe_allow_html=True)
st.markdown("---")

# === Sprawdzenie statusu API ===
try:
    response = requests.get(f"{API_URL}/", timeout=2)
    if response.status_code == 200:
        st.success("✅ API działa poprawnie")
    else:
        st.warning("⚠️ API odpowiada, ale może być problem")
except requests.exceptions.ConnectionError:
    st.error("❌ Nie można połączyć się z API. Upewnij się, że backend działa na http://127.0.0.1:8000")
    st.info("Uruchom backend komendą: `uvicorn app.main:app --reload`")
    st.stop()

st.markdown("---")

# === Formularz danych ===
st.subheader("📝 Wprowadź dane wnioskodawcy")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### Dane osobowe")
    person_age = st.number_input(
        "Wiek",
        min_value=18,
        max_value=90,
        value=30,
        help="Wiek wnioskodawcy (18-90 lat)"
    )
    
    person_income = st.number_input(
        "Roczny dochód ($)",
        min_value=0,
        max_value=1000000,
        value=50000,
        step=1000,
        help="Roczny dochód brutto"
    )
    
    person_home_ownership = st.selectbox(
        "Status mieszkaniowy",
        options=["RENT", "OWN", "MORTGAGE", "OTHER"],
        format_func=lambda x: {
            "RENT": "🏠 Wynajem",
            "OWN": "🏡 Własność",
            "MORTGAGE": "🏦 Hipoteka",
            "OTHER": "📋 Inne"
        }[x],
        help="Status posiadania mieszkania"
    )
    
    person_emp_length = st.number_input(
        "Staż pracy (lata)",
        min_value=0.0,
        max_value=50.0,
        value=5.0,
        step=0.5,
        help="Długość zatrudnienia w latach"
    )

with col2:
    st.markdown("##### Dane pożyczki")
    loan_intent = st.selectbox(
        "Cel pożyczki",
        options=["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"],
        format_func=lambda x: {
            "PERSONAL": "👤 Osobiste",
            "EDUCATION": "🎓 Edukacja",
            "MEDICAL": "🏥 Medyczne",
            "VENTURE": "💼 Biznes",
            "HOMEIMPROVEMENT": "🔧 Remont domu",
            "DEBTCONSOLIDATION": "💰 Konsolidacja długu"
        }[x],
        help="Przeznaczenie pożyczki"
    )
    
    loan_grade = st.selectbox(
        "Ocena kredytowa",
        options=["A", "B", "C", "D", "E", "F", "G"],
        index=1,
        help="Ocena ryzyka pożyczki (A - najlepsza, G - najgorsza)"
    )
    
    loan_amnt = st.number_input(
        "Kwota pożyczki ($)",
        min_value=0,
        max_value=100000,
        value=10000,
        step=500,
        help="Wnioskowana kwota pożyczki"
    )
    
    loan_int_rate = st.number_input(
        "Oprocentowanie (%)",
        min_value=0.0,
        max_value=30.0,
        value=10.0,
        step=0.5,
        help="Roczna stopa procentowa"
    )

with col3:
    st.markdown("##### Historia kredytowa")
    
    # Obliczenie loan_percent_income
    if person_income > 0:
        loan_percent_income = min(loan_amnt / person_income, 0.8)
    else:
        loan_percent_income = 0.0
    
    st.metric(
        "Stosunek pożyczki do dochodu",
        f"{loan_percent_income:.2%}",
        help="Automatycznie obliczony stosunek kwoty pożyczki do rocznego dochodu"
    )
    
    cb_person_default_on_file = st.selectbox(
        "Wcześniejsza niewypłacalność",
        options=["N", "Y"],
        format_func=lambda x: "❌ Nie" if x == "N" else "⚠️ Tak",
        help="Czy wnioskodawca miał wcześniej problemy ze spłatą"
    )
    
    cb_person_cred_hist_length = st.number_input(
        "Długość historii kredytowej (lata)",
        min_value=0.0,
        max_value=50.0,
        value=5.0,
        step=0.5,
        help="Jak długo wnioskodawca ma historię kredytową"
    )

st.markdown("---")

# === Przycisk predykcji ===
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    predict_clicked = st.button(
        "🔮 Sprawdź ryzyko kredytowe",
        type="primary",
        use_container_width=True
    )

if predict_clicked:
    # Przygotowanie danych
    payload = {
        "person_age": person_age,
        "person_income": float(person_income),
        "person_home_ownership": person_home_ownership,
        "person_emp_length": person_emp_length,
        "loan_intent": loan_intent,
        "loan_grade": loan_grade,
        "loan_amnt": float(loan_amnt),
        "loan_int_rate": loan_int_rate,
        "loan_percent_income": loan_percent_income,
        "cb_person_default_on_file": cb_person_default_on_file,
        "cb_person_cred_hist_length": cb_person_cred_hist_length
    }
    
    with st.spinner("Przetwarzanie..."):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                st.markdown("---")
                st.subheader("📊 Wynik analizy")
                
                # Kolory i ikony w zależności od ryzyka
                risk_config = {
                    "niski": {"class": "low-risk", "icon": "✅", "color": "#4CAF50"},
                    "średni": {"class": "medium-risk", "icon": "⚠️", "color": "#FFC107"},
                    "wysoki": {"class": "high-risk", "icon": "🚨", "color": "#F44336"}
                }
                
                config = risk_config.get(result["risk_level"], risk_config["średni"])
                
                # Wyświetlenie wyników
                col_res1, col_res2, col_res3 = st.columns(3)
                
                with col_res1:
                    st.metric(
                        "Predykcja",
                        "Ryzykowny" if result["prediction"] == 1 else "Bezpieczny",
                        delta=None
                    )
                
                with col_res2:
                    st.metric(
                        "Prawdopodobieństwo ryzyka",
                        f"{result['probability']:.1%}"
                    )
                
                with col_res3:
                    st.metric(
                        "Poziom ryzyka",
                        f"{config['icon']} {result['risk_level'].upper()}"
                    )
                
                # Pasek postępu
                st.markdown("##### Wizualizacja ryzyka")
                st.progress(result["probability"])
                
                # Interpretacja
                st.markdown("##### 📋 Interpretacja")
                if result["risk_level"] == "niski":
                    st.success("""
                    **Niskie ryzyko kredytowe** - Wnioskodawca ma korzystny profil kredytowy. 
                    Zalecana pozytywna decyzja kredytowa przy standardowych warunkach.
                    """)
                elif result["risk_level"] == "średni":
                    st.warning("""
                    **Średnie ryzyko kredytowe** - Wnioskodawca wymaga dokładniejszej weryfikacji. 
                    Zalecane dodatkowe zabezpieczenia lub niższa kwota kredytu.
                    """)
                else:
                    st.error("""
                    **Wysokie ryzyko kredytowe** - Wnioskodawca ma niekorzystny profil kredytowy. 
                    Zalecana ostrożność lub odmowa kredytu.
                    """)
                
                # Szczegóły żądania (w expander)
                with st.expander("🔍 Szczegóły zapytania API"):
                    st.json(payload)
                    st.json(result)
                    
            else:
                st.error(f"Błąd API: {response.status_code}")
                st.json(response.json())
                
        except requests.exceptions.Timeout:
            st.error("Timeout - API nie odpowiada")
        except Exception as e:
            st.error(f"Wystąpił błąd: {str(e)}")

# === Stopka ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    Credit Scoring API | AI Credit Scoring Project | 2024
</div>
""", unsafe_allow_html=True)
