from flask import Flask, render_template, request, send_file
from rembg import remove
from PIL import Image
from io import BytesIO
import os
import logging
import urllib.request
from time import perf_counter

app = Flask(__name__)

# Configure structured logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("rmbg-app")

MODEL_PATH = os.path.expanduser('~/.u2net/u2net.onnx')
MODEL_URL = 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx'


def ensure_model_cached():
    """Ensure model exists locally; download once."""
    if os.path.exists(MODEL_PATH):
        return
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    logger.info("Downloading u2net.onnx model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    logger.info(f"Model cached at {MODEL_PATH}")


@app.before_request
def preload_model():
    """Run model check once before first request."""
    ensure_model_cached()
    logger.info("Model ready for inference.")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        start = perf_counter()

        file = request.files.get('file')
        if not file or file.filename == '':
            logger.warning("No file provided in request.")
            return 'No file uploaded', 400

        try:
            input_image = Image.open(file.stream)
            output_image = remove(input_image, post_process_mask=True)
        except Exception as e:
            logger.exception(f"Failed to process image: {e}")
            return 'Error processing image', 500

        img_io = BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)

        elapsed = perf_counter() - start
        logger.info(f"Processed {file.filename} in {elapsed:.3f}s")

        return send_file(img_io, mimetype='image/png',
                         as_attachment=True, download_name='_rmbg.png')

    return render_template('index.html')


if __name__ == '__main__':
    # Preload model for faster cold start when container spins up
    ensure_model_cached()
    logger.info("Starting Flask server on port 5100")
    app.run(host='0.0.0.0', port=5100, debug=False)
