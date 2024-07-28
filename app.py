from io import BytesIO

from flask import Flask, render_template, request, send_file
from PIL import Image
from rembg import remove

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400
        if file:
            input_image = Image.open(file.stream)
            output_image = remove(input_image, post_process_mask=True)
            img_io = BytesIO()
            output_image.save(img_io, 'PNG')
            img_io.seek(0)
            # return send_file(img_io, mimetype='image/png')  # Change download in separate browser tab
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='_rmbg.png')
    return render_template('index.html')

if __name__ == '__main__':
    # Setting debug=True takes much longer to start the server. Use it only when developing. Make sure to remove it before publishing.
    # app.run(host='0.0.0.0', debug=True)
    # use gunicorn.conf.py to set the port instead of hardcoding it here
    app.run(host='0.0.0.0')
    