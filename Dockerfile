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
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# Copy project files
# ---------------------------
COPY . .

# ---------------------------
# Set environment variables
# ---------------------------
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# ---------------------------
# Run Gunicorn on Railway-assigned PORT
# ---------------------------
ENV PORT 8080  # Railway will override this automatically
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "3"]
