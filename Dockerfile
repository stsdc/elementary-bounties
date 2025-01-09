# Use the official Python image from the Docker Hub
FROM python:3.12

# Set environment variables to avoid Python buffering, set poetry path
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.1.6 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create and change to the app directory
WORKDIR /app

# Copy the application files
COPY . .

# Install dependencies
RUN poetry install --no-root

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
