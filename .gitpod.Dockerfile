ARG PYTHON=3.10
FROM python:${PYTHON}-slim

ENV POETRY_VERSION 1.1.11
ENV POETRY_HOME /etc/poetry
ENV PATH "${POETRY_HOME}/bin:${PATH}"

RUN apt-get -y update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ${POETRY_HOME}/bin/poetry config virtualenvs.create "true" \
    && ${POETRY_HOME}/bin/poetry config virtualenvs.in-project "true"
