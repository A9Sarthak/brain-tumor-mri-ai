FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn fastapi python-multipart httpx

# Copy project files
COPY backend /app/backend
COPY src /app/src
COPY models /app/models
COPY results /app/results
COPY data/raw/Testing /app/data/raw/Testing

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
