FROM alpine

ENV CSV_PATH=/input/speedchart.csv

ADD . /app

RUN cd /app \
    && apk -U upgrade \
    && BUILD_DEPS=" \
       gcc \
       python2-dev \
       musl-dev" \
    && apk add ${BUILD_DEPS} python py-pip \
    && pip install -r requirements.txt \
    && apk del ${BUILD_DEPS} \
    && rm -rf /var/cache/apk/* 

VOLUME /input
WORKDIR /app
EXPOSE 8080

ENTRYPOINT python /app/main.py
