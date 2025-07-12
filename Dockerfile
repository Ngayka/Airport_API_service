FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /airport

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
