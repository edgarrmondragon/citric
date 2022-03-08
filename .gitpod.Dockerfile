FROM python:3.10-slim-buster

ENV POETRY_HOME /etc/poetry
ENV PATH "${POETRY_HOME}/bin:${PATH}"

RUN apt-get -y update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ${POETRY_HOME}/bin/poetry config virtualenvs.create "true" \
    && ${POETRY_HOME}/bin/poetry config virtualenvs.in-project "true"

COPY .github/workflows/constraints.txt .
RUN pip install --constraint=.github/workflows/constraints.txt pip
