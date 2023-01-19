FROM python:3.9-slim

COPY . /APP
WORKDIR /APP

RUN chmod -R 777 /APP/docker/hazen_app/start_app.sh

RUN apt-get update && \
  apt-get -y install libpq-dev gcc && \
  pip install psycopg2 && \
  pip install --upgrade pip && \
  python3 -m pip install -r requirements.txt --no-cache-dir \
