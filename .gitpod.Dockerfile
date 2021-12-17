FROM gitpod/workspace-full

ENV POETRY_VERSION 1.1.11
ENV PATH "${HOME}/.poetry/bin:${PATH}"

RUN sudo apt-get -y update \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && $HOME/.poetry/bin/poetry config virtualenvs.create "true" \
    && $HOME/.poetry/bin/poetry config virtualenvs.in-project "true"
