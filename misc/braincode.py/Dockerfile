FROM python:3-alpine

RUN apk add --no-cache socat bash curl

WORKDIR /challenge
COPY chall.py .

COPY flag.txt /tmp/flag.txt
RUN mv /tmp/flag.txt /flag-$(head -c16 /dev/urandom | md5sum | cut -d' ' -f1).txt \
    && chmod 444 /flag-*.txt \
    && adduser -D -s /bin/sh ctf

USER ctf
EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork,max-children=64", "EXEC:python3 -uS /challenge/chall.py,stderr,nofork"]
