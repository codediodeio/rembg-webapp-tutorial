FROM python:3.9

# download this https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx
# copy model to avoid unnecessary download
COPY u2net.onnx /home/.u2net/u2net.onnx

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create logs directory
RUN mkdir -p logs

# Environment variables for authentication
# Set these when running the container to enable authentication
# If not set, the app will run without authentication
ENV BASIC_AUTH_USER=""
ENV BASIC_AUTH_PASS=""
ENV SECRET_KEY=""

# Logging configuration
# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
ENV LOG_LEVEL="INFO"

EXPOSE 5100

CMD ["python", "app.py"]