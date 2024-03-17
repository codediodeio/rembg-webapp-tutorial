#!/bin/bash
docker-compose down
docker image rm ghcr.io/101br03k/rembg-webapp/v1.0-pv-3.12.2-slim
docker build . -t ghcr.io/101br03k/rembg-webapp/v1.0-pv-3.12.2-slim
docker-compose up -d
