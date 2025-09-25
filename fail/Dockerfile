FROM python:3.9-slim-bookworm

# Install Docker CLI (needed to control other containers)
RUN apt-get update && \
    apt-get install -y docker.io && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /fail
COPY . /fail/

