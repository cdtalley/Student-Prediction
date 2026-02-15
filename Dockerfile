# API for Cloud Run. Build generates demo data/models; production: DATA_SOURCE=bigquery.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY src/ src/
COPY config.yaml .

# Generate demo data and train models at build time
RUN mkdir -p data models && python src/train.py

ENV PYTHONPATH=/app
EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
