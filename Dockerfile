FROM python:3.11.1-slim-buster AS base

WORKDIR /app

# Install system dependencies required for building packages and Poetry
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry and move its binary to a directory in PATH
RUN curl -sSL https://install.python-poetry.org | python - && \
    mv /root/.local/bin/poetry /usr/local/bin/

# Copy Poetry files to leverage Docker caching
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to install dependencies into the system environment and skip dev dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --without dev --no-interaction --no-ansi

# Copy the rest of your application code
COPY . /app

FROM base as production
CMD ["python", "manage.py", "runserver"]

FROM base as test
CMD ["pytest", "-v"]
