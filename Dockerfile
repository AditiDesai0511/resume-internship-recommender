# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    SELENIUM_HEADLESS=1

# System deps: Chromium for Selenium, Tesseract for OCR, poppler for pdf2image
RUN apt-get update && apt-get install -y --no-install-recommends \
      chromium \
      chromium-driver \
      tesseract-ocr \
      poppler-utils \
      ca-certificates \
      curl \
 && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt gunicorn

COPY . .

RUN mkdir -p /app/uploads

EXPOSE 5000
ENV PORT=5000
CMD ["sh","-c","gunicorn -w 2 -k gthread --threads 4 --timeout 120 -b 0.0.0.0:${PORT} app:app"]
