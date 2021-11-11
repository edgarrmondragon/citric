FROM python:3.9-slim-buster

ARG POETRY_VERSION=1.1.11
ARG NOX_VERSION=2021.10.1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc

WORKDIR /app

# Install poetry:
RUN pip install poetry==${POETRY_VERSION} nox==${NOX_VERSION}

COPY . .
