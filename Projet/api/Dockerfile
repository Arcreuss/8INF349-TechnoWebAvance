# syntax=docker/dockerfile:1

FROM python:latest

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app
