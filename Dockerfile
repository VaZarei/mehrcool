# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/djangocodes\
    DJANGO_SETTINGS_MODULE=config.settings.production

RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser

WORKDIR /app

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/production.lock.txt

COPY --chown=appuser:appgroup . /app/

# Build-time only placeholders so production settings import; real values come from the runtime env.
RUN DEBUG=False \
    SECRET_KEY="build-only-$(head -c 48 /dev/urandom | base64 | tr -dc 'A-Za-z0-9')" \
    ALLOWED_HOSTS=build.example.com \
    CSRF_TRUSTED_ORIGINS=https://build.example.com \
    SITE_URL=https://build.example.com \
    EMAIL_URL=smtp://user:pass@localhost:25 \
    DEFAULT_FROM_EMAIL=build@example.com \
    LEAD_NOTIFICATION_EMAIL=build@example.com \
    python manage.py collectstatic --noinput \
    && mkdir -p /app/djangocodes/media \
    && chown -R appuser:appgroup /app/djangocodes/staticfiles /app/djangocodes/media

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py createcachetable && exec gunicorn --bind 0.0.0.0:8000 --workers 3 --access-logfile - config.wsgi:application"]
