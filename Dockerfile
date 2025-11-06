# ---- Base image ----
FROM python:3.12-slim

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    libwebp-dev \
    tcl-dev tk-dev python3-tk \
    git curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Set working directory ----
WORKDIR /app

# ---- Copy dependency files ----
COPY requirements.txt .

# ---- Install Python dependencies ----
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Copy project files ----
COPY . .

# ---- Set environment variables ----
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings
ENV PORT=8000

# ---- Collect static files (optional but recommended) ----
RUN python manage.py collectstatic --noinput || true

# ---- Expose the port for Render ----
EXPOSE 8000

# ---- Start Gunicorn ----
# Use shell form so $PORT gets expanded correctly
CMD sh -c "gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3"
