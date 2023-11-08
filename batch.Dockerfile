FROM python:3.9-alpine

RUN apk add --update alpine-sdk && \
   apk add --update --no-cache postgresql-client && \
   apk add --update --no-cache --virtual .tmp-build-deps \
      build-base gcc python3-dev postgresql-dev musl-dev libffi-dev openssl-dev cargo cmake openblas-dev

COPY ./API_SERVICE/batch_service /app/source/batch_service
COPY ./common_libs /app/common_libs
WORKDIR /app/source/batch_service

RUN pip install --no-cache --upgrade pip && pip install -r requirements.txt

ENV APP_ENV=prod
ENV PYTHONPATH=/app/source:/app/common_libs

CMD [ "gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
