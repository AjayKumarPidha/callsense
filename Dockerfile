# Use a Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for some Python libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (to cache deps layer)
COPY requirements.txt .

# Install Python dependencies with larger timeout + retries
RUN pip install --upgrade pip \
    && pip install --default-timeout=1000 --retries=5 --no-cache-dir gunicorn \
    && pip install --default-timeout=1000 --retries=5 --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000
CMD ["gunicorn", "callsense.wsgi:application", "--bind", "0.0.0.0:8000"]
