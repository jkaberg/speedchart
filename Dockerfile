FROM python:3.6.5-alpine

ENV CSV_PATH=/input/speedchart.csv

ADD . /app

RUN cd /app \
    && apk -U upgrade \
    && BUILD_DEPS=" \
       gcc \
       python3-dev \
       musl-dev" \
    && apk add ${BUILD_DEPS} \
    && pip install -r requirements.txt \
    && apk del ${BUILD_DEPS} \
    && rm -rf /var/cache/apk/* 

VOLUME /input
WORKDIR /app
EXPOSE 8080

ENTRYPOINT python /app/main.py
