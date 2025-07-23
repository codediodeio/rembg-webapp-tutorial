from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for
from rembg import remove
from PIL import Image
from io import BytesIO
import base64
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Get auth credentials from environment variables
BASIC_AUTH_USER = os.environ.get('BASIC_AUTH_USER')
BASIC_AUTH_PASS = os.environ.get('BASIC_AUTH_PASS')

# Debug logging
print(f"[DEBUG] BASIC_AUTH_USER: '{BASIC_AUTH_USER}'")
print(f"[DEBUG] BASIC_AUTH_PASS: '{BASIC_AUTH_PASS}'")
print(f"[DEBUG] Auth enabled: {bool(BASIC_AUTH_USER and BASIC_AUTH_PASS)}")

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if no credentials are set
        if not BASIC_AUTH_USER or not BASIC_AUTH_PASS:
            return f(*args, **kwargs)

        # Check if user is already authenticated
        if session.get('authenticated'):
            return f(*args, **kwargs)

        return redirect(url_for('login'))
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Skip auth if no credentials are set
    if not BASIC_AUTH_USER or not BASIC_AUTH_PASS:
        return redirect(url_for('upload_file'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Debug logging
        print(f"[DEBUG] Login attempt - Username: '{username}', Password length: {len(password) if password else 0}")
        print(f"[DEBUG] Expected username: '{BASIC_AUTH_USER}', Expected password length: {len(BASIC_AUTH_PASS) if BASIC_AUTH_PASS else 0}")
        print(f"[DEBUG] Username match: {username == BASIC_AUTH_USER}")
        print(f"[DEBUG] Password match: {password == BASIC_AUTH_PASS}")

        if username == BASIC_AUTH_USER and password == BASIC_AUTH_PASS:
            session['authenticated'] = True
            print("[DEBUG] Login successful")
            return jsonify({'success': True})
        else:
            print("[DEBUG] Login failed - credentials don't match")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/auth-status')
def auth_status():
    # Skip auth if no credentials are set
    if not BASIC_AUTH_USER or not BASIC_AUTH_PASS:
        return jsonify({'auth_required': False, 'authenticated': True})

    return jsonify({
        'auth_required': True,
        'authenticated': session.get('authenticated', False)
    })

@app.route('/', methods=['GET', 'POST'])
@require_auth
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400
        if file:
            # Process the image
            input_image = Image.open(file.stream)
            output_image = remove(input_image, post_process_mask=True)

            # Convert original image to base64
            original_io = BytesIO()
            input_image.save(original_io, 'PNG')
            original_io.seek(0)
            original_b64 = base64.b64encode(original_io.getvalue()).decode('utf-8')

            # Convert processed image to base64
            processed_io = BytesIO()
            output_image.save(processed_io, 'PNG')
            processed_io.seek(0)
            processed_b64 = base64.b64encode(processed_io.getvalue()).decode('utf-8')

            # Check if request wants JSON response (for AJAX)
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'original_image': f"data:image/png;base64,{original_b64}",
                    'processed_image': f"data:image/png;base64,{processed_b64}",
                    'filename': file.filename
                })

            # Default behavior - return file download
            img_io = BytesIO()
            output_image.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='_rmbg.png')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5100)