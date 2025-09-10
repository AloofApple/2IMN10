FROM python:3.9-slim-bookworm
RUN apt-get update
RUN pip3 install rpyc redis

WORKDIR /src
COPY src/ /src/

CMD [ "/bin/bash", "-c", "while true; do bash -l; done" ]