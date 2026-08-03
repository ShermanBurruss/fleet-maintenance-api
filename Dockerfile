# syntax=docker/dockerfile:1

# Use the official slim Python image matching the project's
# current Python major/minor version.
FROM python:3.10-slim


# Prevent Python from creating .pyc files and ensure that application
# output is written directly to the container logs without buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# All remaining commands operate from the application directory.
WORKDIR /app


# Copy dependency definitions separately so Docker can reuse the
# dependency-installation layer when only application code changes.
COPY requirements.txt ./


# Install application dependencies without retaining pip's package cache.
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Copy only the files required to run the API and database migrations.
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app


# Run the application as an unprivileged user rather than root.
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser


# Document the port used by the FastAPI application.
EXPOSE 8000


# Default application command. Docker Compose overrides this command
# so Alembic migrations can run before the API starts.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]