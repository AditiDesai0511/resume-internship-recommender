# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt gunicorn

COPY . .

EXPOSE 5002
ENV PORT=5002
CMD ["sh","-c","gunicorn -w 2 -k gthread --threads 2 --timeout 60 -b 0.0.0.0:${PORT} app:app"]
