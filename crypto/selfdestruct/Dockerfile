FROM python:3-alpine

RUN apk add --no-cache socat \
    && pip install --no-cache-dir pycryptodome colorama

WORKDIR /challenge
COPY chall.py .

EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork,max-children=64", "EXEC:python3 -u chall.py,stderr,nofork"]
