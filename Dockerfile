FROM python:3.13-slim AS base

# Use non-root user for better security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PIP=1

WORKDIR /app

# Install only essential system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary for faster installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Pre-copy and install dependencies separately for layer caching
COPY requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt --system && \
    uv pip install --no-cache-dir gunicorn --system

# Copy app source last to leverage Docker cache
COPY . .

# Pre-download u2net model to prevent runtime fetch
RUN mkdir -p /root/.u2net && \
    curl -L -o /root/.u2net/u2net.onnx \
    https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

EXPOSE 5100

# Use gunicorn instead of Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5100", "--workers", "2", "app:app"]
