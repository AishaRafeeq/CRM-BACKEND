# Use slim Python image
FROM python:3.12-slim

# ---------------------------
# Install system dependencies
# ---------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libpng-dev \
        libfreetype6-dev \
        libwebp-dev \
        tcl-dev tk-dev python3-tk \
        git curl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# Set work directory
# ---------------------------
WORKDIR /app

# ---------------------------
# Copy requirements and install
# ---------------------------
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# Copy project files
# ---------------------------
COPY . .

# ---------------------------
# Expose port for Gunicorn
# ---------------------------
EXPOSE 8000

# ---------------------------
# Set environment variables
# ---------------------------
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# ---------------------------
# Run Gunicorn
# ---------------------------
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
