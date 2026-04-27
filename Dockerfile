FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed for PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Port 7860 is required for Hugging Face Spaces
EXPOSE 7860

# We increased timeout to 300s and limited workers to 1 to save RAM
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "300", "--workers", "1", "--threads", "4", "app:app"]
