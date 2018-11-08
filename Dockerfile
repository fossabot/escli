FROM python:3.6.4-alpine3.7

COPY . /opt

WORKDIR /opt

RUN python3 setup.py install

ENTRYPOINT ["/usr/local/bin/escli"]
