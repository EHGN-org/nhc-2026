FROM python:3-alpine

RUN apk add --no-cache socat

WORKDIR /challenge
COPY chall.py .

EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork,max-children=64", "SYSTEM:python3 chall.py 2>&1"]
