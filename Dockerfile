FROM python:3.9-slim-buster

ARG POETRY_VERSION=1.1.4
ARG NOX_VERSION=2020.8.22

WORKDIR /app

# Install poetry:
RUN pip install poetry==${POETRY_VERSION} nox==${NOX_VERSION}

COPY . .
