FROM python:3.12.0a5-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc

WORKDIR /app/

COPY .github/workflows/constraints.txt .
RUN pip install --constraint=constraints.txt poetry nox

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-dev

COPY . /app/
RUN poetry install --no-dev
