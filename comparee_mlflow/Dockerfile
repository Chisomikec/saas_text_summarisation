FROM python:3.10-slim-buster
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && apt-get purge -y --auto-remove \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY compare.py compare.py
