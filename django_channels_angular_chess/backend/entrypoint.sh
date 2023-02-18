#!/bin/sh

set -e

python manage.py collectstatic --noinput
python manage.py migrate

daphne -b 0.0.0.0 -p 8000 django_chess.asgi:application
