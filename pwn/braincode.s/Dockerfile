FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libc6-dev socat bash curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /challenge
COPY chall.c .
RUN gcc -Wall -Wextra -O0 -o chall chall.c \
    && rm chall.c \
    && apt-get purge -y gcc libc6-dev \
    && apt-get autoremove -y

COPY flag.txt /tmp/flag.txt
RUN mv /tmp/flag.txt /flag-$(head -c16 /dev/urandom | md5sum | cut -d' ' -f1).txt \
    && chmod 444 /flag-*.txt \
    && useradd -m -s /bin/bash ctf

USER ctf
EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork,max-children=64", "SYSTEM:./chall,stderr"]
