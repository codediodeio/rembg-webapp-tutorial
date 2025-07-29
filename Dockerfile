FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# download this https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx
# copy model to avoid unnecessary download
COPY u2net.onnx /home/.u2net/u2net.onnx

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user first
RUN useradd --create-home --shell /bin/bash appuser

# Create logs directory and set proper permissions
RUN mkdir -p logs && \
    touch logs/app.log logs/error.log logs/access.log && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 666 logs/*.log

# Switch to non-root user
USER appuser

# Flask environment configuration (PRODUCTION)
ENV FLASK_ENV="production"
ENV FLASK_DEBUG="False"

# Environment variables for authentication
ENV BASIC_AUTH_USER=""
ENV BASIC_AUTH_PASS=""
ENV SECRET_KEY="production-secret-key-change-me"

# Logging configuration
ENV LOG_LEVEL="INFO"

# Gunicorn configuration
ENV GUNICORN_WORKERS=4
ENV GUNICORN_TIMEOUT=120
ENV GUNICORN_BIND="0.0.0.0:5100"

EXPOSE 5100

# Use Gunicorn for production with stdout/stderr logging to avoid permission issues
CMD gunicorn --workers $GUNICORN_WORKERS \
             --timeout $GUNICORN_TIMEOUT \
             --bind $GUNICORN_BIND \
             --access-logfile - \
             --error-logfile - \
             --capture-output \
             --log-level info \
             app:app