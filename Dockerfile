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

# Tell EasyOCR where to store/find its models — same path at build and runtime
ENV EASYOCR_MODULE_PATH=/app/easyocr_models

WORKDIR /app
COPY . .

# Build React frontend
RUN cd Frontend && npm install && npm run build

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r Backend/Scripts/ExtractorFiles/requirements.txt

# Replace heavy CUDA PyTorch with CPU-only slim build — reduces idle memory by ~500MB
RUN pip install --no-cache-dir \
    torch==2.1.0+cpu \
    torchvision==0.16.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Pre-download EasyOCR model weights into the fixed path baked into the image
RUN mkdir -p /app/easyocr_models && \
    python -c "import easyocr; easyocr.Reader(['en'], gpu=False, model_storage_directory='/app/easyocr_models')"

EXPOSE 10000

CMD gunicorn \
    --chdir Backend/Scripts/ExtractorFiles \
    web_backend:app \
    --bind 0.0.0.0:${PORT:-10000} \
    --timeout 900 \
    --workers 1
