FROM python:3.12-slim

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

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Use shell form so $PORT is expanded
CMD sh -c "gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3"
