FROM golang:1.23-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-flask python3-gunicorn \
    && rm -rf /var/lib/apt/lists/*

COPY readflag.c /tmp/readflag.c
RUN gcc -s -O2 -o /readflag /tmp/readflag.c \
    && chmod 0100 /readflag \
    && rm -f /tmp/readflag.c

# Warm GOCACHE in the image so /tmp can start with a stdlib cache after copy.
RUN mkdir -p /tmp/warm /opt/gocache-seed \
    && printf '%s\n' 'module playground' '' 'go 1.23' > /tmp/warm/go.mod \
    && printf '%s\n' 'package main' '' 'import "fmt"' '' 'func main() { fmt.Println("Hello, NHC") }' > /tmp/warm/main.go \
    && GOPROXY=off CGO_ENABLED=0 GOCACHE=/opt/gocache-seed GOPATH=/tmp/warm-gopath \
       go build -C /tmp/warm -o /dev/null . \
    && rm -rf /tmp/warm /tmp/warm-gopath \
    && chmod -R a+rX /opt/gocache-seed

WORKDIR /app
COPY app.py ./
COPY templates ./templates
COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh

EXPOSE 8080
CMD ["/entrypoint.sh"]
