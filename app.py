from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for
from rembg import remove
from PIL import Image
from io import BytesIO
import base64
import os
import logging
import sys
from functools import wraps
from datetime import datetime

# Configure logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Get log level from environment (default to INFO)
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Separate file handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Reduce noise from external libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    return logging.getLogger(__name__)

# Setup logging
logger = setup_logging()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Get auth credentials from environment variables
BASIC_AUTH_USER = os.environ.get('BASIC_AUTH_USER')
BASIC_AUTH_PASS = os.environ.get('BASIC_AUTH_PASS')

# Startup logging
logger.info("=" * 60)
logger.info("🚀 RMBG Web Application Starting")
logger.info("=" * 60)
logger.info(f"Environment Variables:")
logger.info(f"  - BASIC_AUTH_USER: {'SET' if BASIC_AUTH_USER else 'NOT SET'}")
logger.info(f"  - BASIC_AUTH_PASS: {'SET' if BASIC_AUTH_PASS else 'NOT SET'}")
logger.info(f"  - SECRET_KEY: {'SET' if app.secret_key != 'dev-secret-key-change-in-production' else 'USING DEFAULT'}")
logger.info(f"  - LOG_LEVEL: {os.environ.get('LOG_LEVEL', 'INFO')}")
logger.info(f"Authentication: {'ENABLED' if (BASIC_AUTH_USER and BASIC_AUTH_PASS) else 'DISABLED'}")

# Log password length for debugging (without exposing actual password)
if BASIC_AUTH_PASS:
    logger.debug(f"Password length: {len(BASIC_AUTH_PASS)} characters")
    logger.debug(f"Password starts with: '{BASIC_AUTH_PASS[:3]}...'")

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if no credentials are set
        if not BASIC_AUTH_USER or not BASIC_AUTH_PASS:
            logger.debug("Auth check: No credentials configured, allowing access")
            return f(*args, **kwargs)

        # Check if user is already authenticated
        if session.get('authenticated'):
            logger.debug(f"Auth check: User authenticated via session")
            return f(*args, **kwargs)

        logger.info(f"Auth check: User not authenticated, redirecting to login")
        return redirect(url_for('login'))
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f"Login page accessed - Method: {request.method}, IP: {request.remote_addr}")

    # Skip auth if no credentials are set
    if not BASIC_AUTH_USER or not BASIC_AUTH_PASS:
        logger.info("No auth credentials configured, redirecting to main app")
        return redirect(url_for('upload_file'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        logger.info(f"Login attempt from IP: {request.remote_addr}")
        logger.debug(f"Username provided: '{username}' (length: {len(username)})")
        logger.debug(f"Password provided: length {len(password)}")
        logger.debug(f"Expected username: '{BASIC_AUTH_USER}' (length: {len(BASIC_AUTH_USER)})")
        logger.debug(f"Expected password: length {len(BASIC_AUTH_PASS)}")

        # Check credentials
        username_match = username == BASIC_AUTH_USER
        password_match = password == BASIC_AUTH_PASS

        logger.debug(f"Username match: {username_match}")
        logger.debug(f"Password match: {password_match}")

        if username_match and password_match:
            session['authenticated'] = True
            session['login_time'] = datetime.now().isoformat()
            session['user_ip'] = request.remote_addr
            logger.info(f"✅ Login successful for user '{username}' from IP: {request.remote_addr}")
            return jsonify({'success': True})
        else:
            logger.warning(f"❌ Login failed for user '{username}' from IP: {request.remote_addr}")
            if not username_match:
                logger.debug(f"Username mismatch: got '{username}', expected '{BASIC_AUTH_USER}'")
            if not password_match:
                logger.debug("Password mismatch")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    logger.debug("Serving login page")
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_info = f"IP: {request.remote_addr}"
    if session.get('authenticated'):
        login_time = session.get('login_time', 'unknown')
        user_info += f", Login time: {login_time}"

    logger.info(f"🚪 User logout - {user_info}")
    session.pop('authenticated', None)
    session.pop('login_time', None)
    session.pop('user_ip', None)
    return redirect(url_for('login'))

@app.route('/auth-status')
def auth_status():
    # Skip auth if no credentials are set
    if not BASIC_AUTH_USER or not BASIC_AUTH_PASS:
        logger.debug("Auth status check: No auth required")
        return jsonify({'auth_required': False, 'authenticated': True})

    is_authenticated = session.get('authenticated', False)
    logger.debug(f"Auth status check: Required=True, Authenticated={is_authenticated}")

    return jsonify({
        'auth_required': True,
        'authenticated': is_authenticated
    })

@app.route('/', methods=['GET', 'POST'])
@require_auth
def upload_file():
    if request.method == 'GET':
        logger.info(f"Main page accessed from IP: {request.remote_addr}")
        return render_template('index.html')

    # Handle POST request (file upload)
    start_time = datetime.now()
    logger.info(f"🖼️  Image processing request from IP: {request.remote_addr}")

    try:
        # Validate file upload
        if 'file' not in request.files:
            logger.warning("Upload failed: No file in request")
            return 'No file uploaded', 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("Upload failed: Empty filename")
            return 'No file selected', 400

        if not file:
            logger.warning("Upload failed: No file object")
            return 'No file provided', 400

        # Log file details
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        logger.info(f"Processing file: '{file.filename}' ({file_size:,} bytes)")

        # Process the image
        logger.debug("Opening image with PIL")
        input_image = Image.open(file.stream)
        image_size = input_image.size
        image_mode = input_image.mode
        logger.info(f"Image details: {image_size[0]}x{image_size[1]} pixels, mode: {image_mode}")

        logger.debug("Starting background removal with rembg")
        output_image = remove(input_image, post_process_mask=True)
        logger.debug("Background removal completed")

        # Convert images to base64
        logger.debug("Converting original image to base64")
        original_io = BytesIO()
        input_image.save(original_io, 'PNG')
        original_io.seek(0)
        original_b64 = base64.b64encode(original_io.getvalue()).decode('utf-8')
        original_size = len(original_io.getvalue())

        logger.debug("Converting processed image to base64")
        processed_io = BytesIO()
        output_image.save(processed_io, 'PNG')
        processed_io.seek(0)
        processed_b64 = base64.b64encode(processed_io.getvalue()).decode('utf-8')
        processed_size = len(processed_io.getvalue())

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Processing completed in {processing_time:.2f}s")
        logger.info(f"Original size: {original_size:,} bytes, Processed size: {processed_size:,} bytes")

        # Check if request wants JSON response (for AJAX)
        if request.headers.get('Accept') == 'application/json':
            logger.debug("Returning JSON response for AJAX request")
            return jsonify({
                'original_image': f"data:image/png;base64,{original_b64}",
                'processed_image': f"data:image/png;base64,{processed_b64}",
                'filename': file.filename,
                'processing_time': processing_time,
                'original_size': original_size,
                'processed_size': processed_size
            })

        # Default behavior - return file download
        logger.debug("Returning file download")
        img_io = BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='_rmbg.png')

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Image processing failed after {processing_time:.2f}s: {str(e)}", exc_info=True)
        return jsonify({'error': 'Image processing failed', 'message': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url} from IP: {request.remote_addr}")
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)} from IP: {request.remote_addr}", exc_info=True)
    return "Internal server error", 500

if __name__ == '__main__':
    logger.info("🌟 Starting Flask development server")
    logger.info(f"Server will be available at: http://0.0.0.0:5100")
    logger.info("=" * 60)

    try:
        app.run(host='0.0.0.0', debug=True, port=5100)
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server startup failed: {str(e)}", exc_info=True)
    finally:
        logger.info("👋 Application shutdown")
        logger.info("=" * 60)