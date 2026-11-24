# MailMind AI — Backend image
FROM python:3.12-slim AS development

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM development AS production

ENV APP_ENV=production \
    APP_DEBUG=false \
    PYTHONUNBUFFERED=1 \
    FORWARDED_ALLOW_IPS="*"

# The trained model file is gitignored, so build it into the image (a few seconds on this dataset)
RUN mkdir -p ml/artifacts && python ml/train.py

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
