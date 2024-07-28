FROM python:3.9-slim

# download this https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx
# copy model to avoid unnecessary download
RUN apt update && apt install wget -y
RUN mkdir /root/.u2net && wget -O /root/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5100

# CMD ["python", "app.py"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]