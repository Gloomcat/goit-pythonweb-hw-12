# Use a minimal Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Copy the startup script
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

# Use the startup script as the container's entrypoint
CMD ["/usr/local/bin/run.sh"]
