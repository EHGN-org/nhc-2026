# Bullseye is glibc 2.31. PyInstaller links against the image libc, so
# building on an old glibc keeps the binary runnable on newer hosts.
FROM python:3.12-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pyinstaller pycryptodome colorama \
    && useradd --uid 1000 --create-home --shell /bin/bash builder

WORKDIR /app
USER 1000

CMD ["./build.sh"]
