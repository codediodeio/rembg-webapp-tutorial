# Background Removal Web App

A modern Flask web application for removing backgrounds from images using [Rembg](https://github.com/danielgatis/rembg). Features a clean web interface with optional authentication and comprehensive logging.

![Background Removal Demo](https://img.shields.io/badge/Demo-Background%20Removal-blue)

> **Fork Information**: This is an enhanced fork of the original [rembg-webapp-tutorial](https://github.com/codediodeio/rembg-webapp-tutorial) by [@codediodeio](https://github.com/codediodeio). This version includes additional features like authentication, comprehensive logging, multiple Docker configurations, and production-ready deployment options.

## 🎯 Features

- **Web Interface**: Modern, responsive UI for easy image uploads
- **Background Removal**: Powered by AI models via Rembg library
- **Authentication**: Optional basic authentication for secure access
- **Docker Support**: Multiple deployment options with containerization
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Production Ready**: Configurable for development and production environments

## 🚀 Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd rembg-webapp-tutorial
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the app**: Open http://localhost:5100 in your browser

Watch the [tutorial](https://youtu.be/cw34KMPSt4k) on YouTube for a step-by-step walkthrough.

## 🐳 Docker Deployment

### Docker Compose (Recommended)

The easiest way to deploy is using Docker Compose:

1. **Build the image**:
   ```bash
   docker build -t my-rembg-app .
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access the app**: Open http://localhost:5101

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Stop the service**:
   ```bash
   docker-compose down
   ```

The included `docker-compose.yml` configures:
- **Port mapping**: 5101 (host) → 5100 (container)
- **Authentication**: Enabled with admin/strong_pass
- **Production mode**: Optimized for production use
- **Log persistence**: Logs saved to `./logs` directory
- **Auto-restart**: Container restarts automatically

### Manual Docker Run

#### Basic Docker Run
```bash
# Build the image
docker build -t rembg-webapp .

# Run without authentication
docker run -p 5100:5100 rembg-webapp

# Run with authentication
docker run -p 5100:5100 \
  -e BASIC_AUTH_USER=admin \
  -e BASIC_AUTH_PASS=secure_password \
  -e SECRET_KEY=your_secret_key \
  rembg-webapp
```

#### Production Docker Run
```bash
docker run -p 5100:5100 \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=False \
  -e BASIC_AUTH_USER=admin \
  -e BASIC_AUTH_PASS=secure_password \
  -e SECRET_KEY=your_production_secret_key \
  -e LOG_LEVEL=INFO \
  rembg-webapp
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment mode (`development`/`production`) | `development` | No |
| `FLASK_DEBUG` | Enable debug mode (`True`/`False`) | `True` (dev), `False` (prod) | No |
| `BASIC_AUTH_USER` | Username for authentication | None | No |
| `BASIC_AUTH_PASS` | Password for authentication | None | No |
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key-change-in-production` | Recommended |
| `LOG_LEVEL` | Logging level (`DEBUG`/`INFO`/`WARNING`/`ERROR`) | `INFO` | No |

### Authentication

- **Optional**: Set both `BASIC_AUTH_USER` and `BASIC_AUTH_PASS` to enable authentication
- **Disabled**: Leave these variables unset for open access
- **Sessions**: Authenticated users stay logged in for 1 hour

## 📁 Project Structure

```
rembg-webapp-tutorial/
├── app.py                    # Main Flask application
├── basic.py                  # Basic example script
├── requirements.txt          # Python dependencies
├── requirements-prod.txt     # Production dependencies
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Standard Docker configuration
├── Dockerfile.prod          # Production Docker configuration
├── Dockerfile.prod-simple   # Simplified production Docker
├── templates/
│   ├── index.html           # Main upload interface
│   └── login.html           # Authentication page
├── static/
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── u2net.onnx              # AI model file (168MB)
└── logs/                   # Application logs (development)
```

## 🔧 Usage

### Web Interface
1. Navigate to http://localhost:5100
2. Log in if authentication is enabled
3. Upload an image using the file selector
4. Wait for processing (typically 2-5 seconds)
5. Download the processed image with background removed

### API Endpoint
The app also supports programmatic access:

```bash
# Upload image via API
curl -X POST \
  -F "file=@your-image.jpg" \
  -H "Accept: application/json" \
  http://localhost:5100/
```

## 🛠️ Development

### File Structure
- `app.py`: Main application with comprehensive logging and authentication
- `basic.py`: Simple command-line example
- `templates/`: HTML templates for the web interface
- `static/`: CSS and JavaScript assets

### Logging
- **Development**: Logs to console and files (`logs/app.log`, `logs/error.log`)
- **Production**: Console logging only
- **Levels**: Configurable via `LOG_LEVEL` environment variable

### Dependencies
- **Flask**: Web framework
- **Rembg**: Background removal AI
- **Pillow**: Image processing
- **ONNX Runtime**: AI model execution

## 🚨 Production Considerations

1. **Set a secure SECRET_KEY**: Generate a random secret key for production
2. **Enable authentication**: Set strong credentials via environment variables
3. **Use production environment**: Set `FLASK_ENV=production`
4. **Monitor logs**: Configure proper log aggregation
5. **Resource limits**: The AI model requires significant memory (recommend 2GB+ RAM)

## 📋 Requirements

- Python 3.7+
- 2GB+ RAM (for AI model)
- Modern web browser
- Docker (optional, for containerized deployment)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

---

**Note**: The AI model file (`u2net.onnx`) is approximately 168MB and will be downloaded automatically on first run if not present.