# Raport z konteneryzacji (Docker)

## 1. Lista kontenerów i ich funkcje

### 🏗️ Backend (`ai_backend`)
- **Obraz**: Python 3.10-slim
- **Funkcja**: API oparte na FastAPI służące do oceny ryzyka kredytowego.
- **Port**: 8000
- **Kluczowe pliki**:
    - `app/main.py`: Kod aplikacji backendowej.
    - `data/06_models/best_model.pkl`: Model uczenia maszynowego.
    - `data/02_intermediate/clean_data.csv`: Dane do kalibracji scalera.
- **Zależności**: `fastapi`, `uvicorn`, `scikit-learn`, `pandas`.

### 🎨 Frontend (`ai_frontend`)
- **Obraz**: Python 3.10-slim
- **Funkcja**: Interfejs użytkownika stworzony w Streamlit.
- **Port**: 8501
- **Komunikacja**: Łączy się z backendem pod adresem `http://backend:8000` (wewnątrz sieci Docker).
- **Zależności**: `streamlit`, `requests`.

### 🔄 Airflow (Istniejące usługi)
- **Funkcja**: Orkiestracja procesów ML (ETL, trenowanie).
- **Usługi**: `postgres`, `airflow-webserver`, `airflow-scheduler`, `airflow-init`.
- **Status**: Zachowano kompatybilność z istniejącą konfiguracją w `docker-compose.yml`.

---

## 2. Komendy budowania i uruchomienia

### Budowa i uruchomienie (Docker Compose)
Aby uruchomić cały system (Backend + Frontend + Airflow):
```bash
docker-compose up --build -d
```
Parametr `-d` uruchamia kontenery w tle.



