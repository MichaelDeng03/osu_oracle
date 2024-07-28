# Dockerfile for data_collector
FROM python:3.9

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application code
COPY . /app

# Command to run the application
CMD ["poetry", "run", "python", "data_collector.py"]