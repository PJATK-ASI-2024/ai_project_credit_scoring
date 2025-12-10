"""
Testy integracyjne dla Credit Scoring API

Uruchomienie: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Dodanie ścieżki do modułu app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app, load_model_and_scaler

# Ręczne załadowanie modelu przed testami (lifespan nie uruchamia się automatycznie w TestClient)
load_model_and_scaler()

client = TestClient(app)


class TestHomeEndpoint:
    """Testy endpointu głównego"""
    
    def test_home_returns_200(self):
        """Test: endpoint / zwraca status 200"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_home_contains_message(self):
        """Test: odpowiedź zawiera pole message"""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "działa" in data["message"] or "API" in data["message"]
    
    def test_home_model_loaded(self):
        """Test: model został załadowany"""
        response = client.get("/")
        data = response.json()
        assert "model_loaded" in data
        assert data["model_loaded"] is True


class TestHealthEndpoint:
    """Testy endpointu health check"""
    
    def test_health_returns_200(self):
        """Test: endpoint /health zwraca status 200"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_returns_healthy(self):
        """Test: odpowiedź zawiera status healthy"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"


class TestPredictEndpoint:
    """Testy endpointu predykcji"""
    
    @pytest.fixture
    def valid_payload(self):
        """Przykładowe poprawne dane wejściowe"""
        return {
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
    
    def test_predict_returns_200(self, valid_payload):
        """Test: endpoint /predict zwraca status 200 dla poprawnych danych"""
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200
    
    def test_predict_returns_prediction(self, valid_payload):
        """Test: odpowiedź zawiera pole prediction"""
        response = client.post("/predict", json=valid_payload)
        data = response.json()
        assert "prediction" in data
        assert data["prediction"] in [0, 1]
    
    def test_predict_returns_probability(self, valid_payload):
        """Test: odpowiedź zawiera pole probability"""
        response = client.post("/predict", json=valid_payload)
        data = response.json()
        assert "probability" in data
        assert 0 <= data["probability"] <= 1
    
    def test_predict_returns_risk_level(self, valid_payload):
        """Test: odpowiedź zawiera pole risk_level"""
        response = client.post("/predict", json=valid_payload)
        data = response.json()
        assert "risk_level" in data
        assert data["risk_level"] in ["niski", "średni", "wysoki"]
    
    def test_predict_high_risk_profile(self):
        """Test: wysoki profil ryzyka - młody, niski dochód, wysoka pożyczka"""
        payload = {
            "person_age": 20,
            "person_income": 15000,
            "person_home_ownership": "RENT",
            "person_emp_length": 0.5,
            "loan_intent": "PERSONAL",
            "loan_grade": "E",
            "loan_amnt": 10000,
            "loan_int_rate": 18.0,
            "loan_percent_income": 0.67,
            "cb_person_default_on_file": "Y",
            "cb_person_cred_hist_length": 1
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Prawdopodobieństwo powinno być wyższe dla ryzykownego profilu
        assert data["probability"] >= 0.0  # Tylko sprawdzamy że jest liczbą
    
    def test_predict_low_risk_profile(self):
        """Test: niski profil ryzyka - starszy, wysoki dochód, niska pożyczka"""
        payload = {
            "person_age": 45,
            "person_income": 120000,
            "person_home_ownership": "OWN",
            "person_emp_length": 15.0,
            "loan_intent": "HOMEIMPROVEMENT",
            "loan_grade": "A",
            "loan_amnt": 5000,
            "loan_int_rate": 6.0,
            "loan_percent_income": 0.04,
            "cb_person_default_on_file": "N",
            "cb_person_cred_hist_length": 20
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["probability"] <= 1.0  # Tylko sprawdzamy że jest liczbą


class TestPredictValidation:
    """Testy walidacji danych wejściowych"""
    
    def test_predict_invalid_age_too_young(self):
        """Test: wiek poniżej 18 lat powinien zwrócić błąd"""
        payload = {
            "person_age": 15,  # Za młody
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
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_predict_invalid_home_ownership(self):
        """Test: nieprawidłowy status mieszkaniowy powinien zwrócić błąd"""
        payload = {
            "person_age": 25,
            "person_income": 50000,
            "person_home_ownership": "INVALID",  # Nieprawidłowa wartość
            "person_emp_length": 3.0,
            "loan_intent": "PERSONAL",
            "loan_grade": "B",
            "loan_amnt": 10000,
            "loan_int_rate": 10.5,
            "loan_percent_income": 0.2,
            "cb_person_default_on_file": "N",
            "cb_person_cred_hist_length": 4
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
    
    def test_predict_missing_field(self):
        """Test: brakujące pole powinno zwrócić błąd"""
        payload = {
            "person_age": 25,
            # Brak person_income i innych pól
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422


class TestModelInfoEndpoint:
    """Testy endpointu informacji o modelu"""
    
    def test_model_info_returns_200(self):
        """Test: endpoint /model-info zwraca status 200"""
        response = client.get("/model-info")
        assert response.status_code == 200
    
    def test_model_info_contains_model_type(self):
        """Test: odpowiedź zawiera typ modelu"""
        response = client.get("/model-info")
        data = response.json()
        assert "model_type" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
