FROM python:3.11-slim

# --------------------
# Python runtime flags
# --------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --------------------
# Prometheus (CRITICAL for Gunicorn)
# --------------------
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
RUN mkdir -p /tmp/prometheus

# --------------------
# Application setup
# --------------------
WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY templates/ templates/

# Create model directory inside container
RUN mkdir -p heart_disease_model

# Copy model artifacts (FIXED PATHS ✅)
COPY heart_disease_model/model.joblib heart_disease_model/
COPY heart_disease_model/scaler.joblib heart_disease_model/

# Expose application port
EXPOSE 5007

# --------------------
# Run with Gunicorn (Prometheus-safe)
# --------------------
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5007", \
     "--workers", "2", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "app:app"]
