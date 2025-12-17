# Etap 1 — obraz bazowy
FROM python:3.10-slim

# Ustaw katalog roboczy
WORKDIR /workspace

# Kopiowanie zależności
COPY ./requirements.txt .

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install fastapi uvicorn pydantic

# Kopiowanie kodu aplikacji
COPY ./app ./app

# Kopiowanie modelu i danych
COPY ./data/06_models/best_model.pkl ./data/06_models/best_model.pkl
COPY ./data/02_intermediate/clean_data.csv ./data/02_intermediate/clean_data.csv

# Zmiana katalogu na app, aby uvicorn widział main.py
WORKDIR /workspace/app

# Port API
EXPOSE 8000

# Komenda startowa
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
