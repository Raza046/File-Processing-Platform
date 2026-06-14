#!/bin/sh
python manage.py collectstatic --noinput

python manage.py migrate
# exec python manage.py runserver 0.0.0.0:8000

# exec gunicorn config.wsgi:application --bind 0.0.0.0:8000

# IMPORTANT: allow CMD to decide what runs
exec "$@"

# CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
