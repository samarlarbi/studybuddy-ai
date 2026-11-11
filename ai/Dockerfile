# Base image: Python on a small Linux
FROM python:3.13-slim

WORKDIR /app

# Copy the dependency list first so Docker can cache the install step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Where the embedding model is stored (mounted as a volume in compose)
ENV MODEL_CACHE_DIR=/models

EXPOSE 8000

# 0.0.0.0 = accept connections from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]