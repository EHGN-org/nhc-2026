FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py gen.py .
COPY templates/ templates/
COPY js/ js/

EXPOSE 8080
CMD ["gunicorn", "--preload", "-w", "2", "--threads", "4", "-b", "0.0.0.0:8080", "app:app"]
