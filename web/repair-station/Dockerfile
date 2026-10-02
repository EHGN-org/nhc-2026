FROM python:3.12-alpine

RUN apk add --no-cache bash curl

RUN adduser -D -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh \
    && touch /flag.txt \
    && chown appuser:appuser /flag.txt \
    && chmod 0644 /flag.txt

USER appuser

EXPOSE 1337

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-u", "app.py"]
