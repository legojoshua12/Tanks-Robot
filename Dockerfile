FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY src /app/src
COPY requirements.txt /app
COPY config.ini /app
COPY main.py /app

RUN pip install -r requirements.txt
