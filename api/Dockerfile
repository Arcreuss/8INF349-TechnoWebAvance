# syntax=docker/dockerfile:1

FROM python:3.11.3-alpine3.16

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

RUN ["flask", "init-db"]
CMD ["flask", "run"]
