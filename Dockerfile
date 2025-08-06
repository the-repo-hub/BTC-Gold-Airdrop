FROM python:3.13-slim as runtime
LABEL authors="howard"
#poetry
RUN pip install --no-cache-dir poetry==1.8.5
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app/BTC-Gold
COPY pyproject.toml messages_config.yaml .env ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-interaction --no-ansi
ENV PATH="/app/BTC-Gold/.venv/bin:$PATH"
WORKDIR /app/BTC-Gold/src
COPY ./src .
ENTRYPOINT ["python", "main.py"]