FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN DJANGO_SECRET_KEY=build python manage.py collectstatic --noinput

RUN useradd --system --no-create-home --uid 10001 app
USER 10001

# Cloud Run sets $PORT (defaults to 8080)
ENV PORT=8080
CMD python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 0
