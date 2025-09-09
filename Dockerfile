# syntax=docker/dockerfile:1

FROM python:3.9.16-alpine3.16
WORKDIR /code

ARG user
ARG uid

RUN apk update
RUN apk upgrade
RUN apk add  --update ca-certificates && update-ca-certificates tzdata
ENV TZ=America/Bahia
RUN rm -rf /var/cache/apk/*

ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8


# Config openssl
RUN apk add --no-cache autoconf make g++ perl gnupg nano curl
RUN apk add --no-cache openssl openssl-dev


ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

VOLUME ["/code"]

EXPOSE 80
COPY . .
# Run Gunicorn instead of Flask development server
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app", "--timeout", "1000"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "views:app", "--timeout", "1000", "--access-logfile", "/code/logs/access.log", "--error-logfile", "/code/logs/error.log"]
