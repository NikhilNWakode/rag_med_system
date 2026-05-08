FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/download_models.py .
RUN python download_models.py && rm download_models.py

COPY backend/ .

EXPOSE 8000

CMD ["python", "-c", "import os; os.system(f'uvicorn app.main:app --host 0.0.0.0 --port {os.environ.get(\"PORT\", \"8000\")}')"]
