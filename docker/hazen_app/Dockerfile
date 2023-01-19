FROM python:3.9-slim

COPY . /APP
WORKDIR /APP

RUN chmod -R 777 /APP/docker/hazen_app/start_app.sh

RUN apt-get update && \
    apt-get -y install libpq-dev gcc

RUN pip install --upgrade pip && \
    pip install psycopg2 && \
    python3 -m pip install -r requirements.txt
