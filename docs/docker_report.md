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

Aby uruchomić **tylko** aplikację (Backend + Frontend):
```bash
docker-compose up --build -d backend frontend
```

### Ręczne budowanie obrazów (opcjonalnie)
Backend:
```bash
docker build -t ai_project_backend -f app/Dockerfile .
```

Frontend:
```bash
docker build -t ai_project_frontend -f frontend/Dockerfile .
```

---

## 3. Linki do DockerHub

Obrazy zostały przygotowane do wypchnięcia (push) na DockerHub.

**Tagowanie obrazów:**
```bash
docker tag ai_project_backend maciejwoj/ai_project_backend:latest
docker tag ai_project_frontend maciejwoj/ai_project_frontend:latest
```

**Publikacja:**
```bash
docker push maciejwoj/ai_project_backend:latest
docker push maciejwoj/ai_project_frontend:latest
```

## 4. Wdrożenie w chmurze (Render.com)

Projekt zawiera plik `render.yaml` (Blueprint), który automatyzuje wdrożenie backendu i frontendu.

### Instrukcja wdrożenia:
1.  Wypchnij kod projektu na swoje repozytorium GitHub.
2.  Zaloguj się na [Render.com](https://render.com/).
3.  Kliknij **New +** -> **Blueprint**.
4.  Połącz swoje repozytorium GitHub.
5.  Render wykryje plik `render.yaml` i zaproponuje utworzenie dwóch serwisów:
    - `ai-credit-scoring-backend`
    - `ai-credit-scoring-frontend`
6.  Kliknij **Apply**.
7.  Po zakończeniu budowania otrzymasz dwa linki. Aplikacja frontendowa automatycznie połączy się z backendem dzięki zmiennej środowiskowej `API_URL`.
