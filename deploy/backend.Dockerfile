FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend /app
RUN pip install --upgrade pip && pip install -e . && pip install -e .[tests]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
