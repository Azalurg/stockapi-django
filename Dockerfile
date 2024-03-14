# https://medium.com/vantageai/how-to-make-your-python-docker-images-secure-fast-small-b3a6870373a0

FROM python:3.10.12-slim as builder
ENV PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

FROM python:3.10.12-slim as worker

WORKDIR /app

COPY --from=builder /app/requirements.txt .


RUN set -ex \
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Upgrade the package index and install security upgrades
    && apt-get update \
    && apt-get upgrade -y \
    # Install dependencies
    && pip install -r requirements.txt \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN chown -R appuser:appgroup /app

USER appuser
