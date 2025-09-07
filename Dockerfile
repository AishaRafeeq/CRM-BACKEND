FROM python:3.12-slim

# Install system dependencies for Pillow and other common packages
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libwebp-dev \
        libtiff-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        tcl-dev tk-dev python3-tk \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Command to run
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
