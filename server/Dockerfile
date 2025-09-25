FROM python:3.9-slim-bookworm

RUN apt-get update 
RUN pip3 install rpyc redis

WORKDIR /server
COPY . /server/