"""
Credit Scoring API - FastAPI Backend

This API provides predictions for credit risk assessment using a trained ML model.
It includes full preprocessing integration to transform raw user inputs.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# === Ścieżki do plików ===
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATHS = [
    BASE_DIR / "data" / "06_models" / "best_model.pkl",
    BASE_DIR / "data" / "06_models" / "custom_model.pkl",
    BASE_DIR / "data" / "06_models" / "baseline_model.pkl",
]
CLEAN_DATA_PATH = BASE_DIR / "data" / "02_intermediate" / "clean_data.csv"

# === Zmienne globalne ===
model = None
scaler = None
feature_columns = None
model_path_used = None


def load_model_and_scaler():
    """Wczytanie modelu i dopasowanie scalera"""
    global model, scaler, feature_columns, model_path_used
    
    # Próba wczytania modelu z różnych ścieżek (fallback)
    import warnings
    for model_path in MODEL_PATHS:
        if model_path.exists():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    with open(model_path, "rb") as f:
                        model = pickle.load(f)
                model_path_used = model_path
                print(f"✅ Model wczytany z: {model_path.name}")
                break
            except Exception as e:
                print(f"⚠️ Nie można wczytać {model_path.name}: {e}")
                continue
    
    if model is None:
        raise RuntimeError(f"Nie można wczytać żadnego modelu")
    
    # Wczytanie danych do dopasowania scalera
    if not CLEAN_DATA_PATH.exists():
        raise RuntimeError(f"Dane do scalera nie znalezione: {CLEAN_DATA_PATH}")
    
    clean_data = pd.read_csv(CLEAN_DATA_PATH)
    
    # Kolumny numeryczne do skalowania (bez target i ID)
    exclude_cols = {"loan_status", "_row_id"}
    num_cols = clean_data.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = [c for c in num_cols if c not in exclude_cols]
    
    # Dopasowanie scalera
    scaler = StandardScaler()
    scaler.fit(clean_data[num_cols])
    
    # Zapamiętanie kolejności cech
    feature_columns = num_cols
    
    print(f"✅ Model wczytany: {type(model).__name__}")
    print(f"✅ Scaler dopasowany na {len(feature_columns)} cechach numerycznych")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager - ładowanie modelu przy starcie"""
    load_model_and_scaler()
    yield
    # Cleanup (opcjonalnie)


# === Konfiguracja aplikacji ===
app = FastAPI(
    title="Credit Scoring API",
    description="API do oceny ryzyka kredytowego z wykorzystaniem modelu ML",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - pozwalamy na połączenia z frontendu Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Model danych wejściowych ===
class CreditInput(BaseModel):
    """Dane wejściowe do predykcji ryzyka kredytowego"""
    person_age: int = Field(..., ge=18, le=90, description="Wiek osoby (18-90 lat)")
    person_income: float = Field(..., ge=0, description="Roczny dochód")
    person_home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER"] = Field(..., description="Status mieszkaniowy")
    person_emp_length: float = Field(..., ge=0, description="Długość zatrudnienia w latach")
    loan_intent: Literal["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"] = Field(..., description="Cel pożyczki")
    loan_grade: Literal["A", "B", "C", "D", "E", "F", "G"] = Field(..., description="Ocena pożyczki")
    loan_amnt: float = Field(..., ge=0, description="Kwota pożyczki")
    loan_int_rate: float = Field(..., ge=0, le=100, description="Oprocentowanie pożyczki (%)")
    loan_percent_income: float = Field(..., ge=0, le=1, description="Stosunek pożyczki do dochodu")
    cb_person_default_on_file: Literal["Y", "N"] = Field(..., description="Czy osoba miała wcześniej niewypłacalność")
    cb_person_cred_hist_length: float = Field(..., ge=0, description="Długość historii kredytowej w latach")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "person_age": 25,
                    "person_income": 50000,
                    "person_home_ownership": "RENT",
                    "person_emp_length": 3.0,
                    "loan_intent": "PERSONAL",
                    "loan_grade": "B",
                    "loan_amnt": 10000,
                    "loan_int_rate": 10.5,
                    "loan_percent_income": 0.2,
                    "cb_person_default_on_file": "N",
                    "cb_person_cred_hist_length": 4
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Odpowiedź z predykcją"""
    prediction: int = Field(..., description="Predykcja: 0 = brak ryzyka, 1 = ryzyko")
    probability: float = Field(..., description="Prawdopodobieństwo ryzyka (0-1)")
    risk_level: str = Field(..., description="Poziom ryzyka: niski/średni/wysoki")





def create_age_bin(age: int) -> str:
    """Tworzenie binu wiekowego zgodnie z preprocessing pipeline"""
    if age <= 25:
        return "18-25"
    elif age <= 35:
        return "26-35"
    elif age <= 45:
        return "36-45"
    elif age <= 60:
        return "46-60"
    else:
        return "60+"


def create_income_bin(income: float) -> str:
    """Tworzenie binu dochodowego na podstawie stałych progów"""
    if income <= 35000:
        return "(3999.999, 35000.0]"
    elif income <= 49000:
        return "(35000.0, 49000.0]"
    elif income <= 63000:
        return "(49000.0, 63000.0]"
    elif income <= 86000:
        return "(63000.0, 86000.0]"
    elif income <= 138000:
        return "(86000.0, 138000.0]"
    else:
        return "(138000.0, 140250.0]"



@app.get("/")
def home():
    """Endpoint sprawdzający status API"""
    return {
        "message": "Credit Scoring API działa poprawnie 🚀",
        "model_loaded": model is not None,
        "scaler_fitted": scaler is not None
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: CreditInput):
    """
    Endpoint do predykcji ryzyka kredytowego.
    
    Przyjmuje surowe dane użytkownika, przetwarza je zgodnie z pipeline'm
    preprocessingu i zwraca predykcję modelu.
    """
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model lub scaler nie zostały wczytane")
    
    try:
        # Tworzenie DataFrame z danymi wejściowymi
        input_dict = data.model_dump()
        
        # Tworzenie binów (feature engineering)
        input_dict["person_age_bin"] = create_age_bin(input_dict["person_age"])
        input_dict["person_income_bin"] = create_income_bin(input_dict["person_income"])
        
        # DataFrame
        df = pd.DataFrame([input_dict])
        
        # Skalowanie kolumn numerycznych
        num_cols_in_df = [c for c in feature_columns if c in df.columns]
        df[num_cols_in_df] = scaler.transform(df[num_cols_in_df])
        
        # Usunięcie kolumny target jeśli istnieje (nie powinna)
        if "loan_status" in df.columns:
            df = df.drop(columns=["loan_status"])
        
        # Upewnienie się, że mamy wszystkie cechy wymagane przez model
        if hasattr(model, "feature_names_in_"):
            # Dla modeli które pamiętają nazwy cech
            missing = set(model.feature_names_in_) - set(df.columns)
            
            # Dodanie brakujących kolumn z wartościami domyślnymi
            for col in missing:
                if col == "_row_id":
                    # _row_id to identyfikator wiersza, nie cecha - dodajemy dummy
                    df[col] = 0
                else:
                    # Inne brakujące kolumny - ustawiamy na 0.0
                    df[col] = 0.0
                    print(f"⚠️ Dodano brakującą cechę '{col}' z wartością domyślną 0")
            
            df = df[model.feature_names_in_]
        
        # Predykcja
        prediction = int(model.predict(df)[0])
        
        # Prawdopodobieństwo (jeśli model to obsługuje)
        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(df)[0][1])
        else:
            probability = float(prediction)
        
        # Interpretacja ryzyka
        if probability < 0.3:
            risk_level = "niski"
        elif probability < 0.7:
            risk_level = "średni"
        else:
            risk_level = "wysoki"
        
        return PredictionResponse(
            prediction=prediction,
            probability=round(probability, 4),
            risk_level=risk_level
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania: {str(e)}")


@app.get("/model-info")
def model_info():
    """Informacje o załadowanym modelu"""
    if model is None:
        return {"error": "Model nie został wczytany"}
    
    info = {
        "model_type": type(model).__name__,
        "feature_columns": feature_columns if feature_columns else []
    }
    
    if hasattr(model, "feature_names_in_"):
        info["model_features"] = list(model.feature_names_in_)
    
    if hasattr(model, "n_features_in_"):
        info["n_features"] = model.n_features_in_
    
    return info
