FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /airport

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /files/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    admin

RUN chown -R admin /files/media
RUN chmod 755 /files/media

USER admin