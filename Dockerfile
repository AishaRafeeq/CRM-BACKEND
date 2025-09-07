# Use a Python base image
FROM python:3.12-slim

# Install system libraries needed by Pillow
RUN apt-get update && \
    apt-get install -y libjpeg62-turbo libpng-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Command to run Django
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
