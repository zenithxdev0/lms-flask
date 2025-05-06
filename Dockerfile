# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=run.py
ENV FLASK_DEBUG=0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the project code into the container
COPY . .

# Create directory for database if it doesn't exist
RUN mkdir -p /app/instance && \
    chown -R appuser:appuser /app

# Expose the port the app runs on
EXPOSE 5000

# Switch to non-root user
USER appuser

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]