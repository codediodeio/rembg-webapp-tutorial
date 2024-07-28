A simple flask app to remove the background of an image with [Rembg](https://github.com/danielgatis/rembg)

Watch the [tutorial](https://youtu.be/cw34KMPSt4k) on YouTube

## Run it

```
pip install -r requirements.txt
gunicorn -c gunicorn.conf.py app:app
```

## Run using docker

```
docker build -t someName .
docker run -it -p 5100:5100 someName
```
