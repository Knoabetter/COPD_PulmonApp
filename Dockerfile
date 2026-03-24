FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

# Build React frontend
RUN cd Frontend && npm install && npm run build

# Install Python dependencies (CPU-only torch to avoid CUDA bloat on free tier)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r Backend/Scripts/ExtractorFiles/requirements.txt

# Pre-download EasyOCR models so they are baked into the image (no runtime downloads)
RUN python -c "import easyocr; easyocr.Reader(['en'])"

EXPOSE 10000

CMD gunicorn \
    --chdir Backend/Scripts/ExtractorFiles \
    web_backend:app \
    --bind 0.0.0.0:${PORT:-10000} \
    --timeout 300 \
    --workers 1
