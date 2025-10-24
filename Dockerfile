FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.0

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Install the application
RUN poetry install --no-interaction --no-ansi

# Install Playwright browsers and dependencies (must be BEFORE switching user)
RUN playwright install chromium \
    && playwright install-deps chromium

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Install browsers for the user too
USER appuser
RUN playwright install chromium

# Default command
CMD ["python", "-m", "src.ingest.runner"]
