#!/bin/sh

set -e

python manage.py collectstatic --noinput

daphne -b 127.0.0.1 -p 80 django_chess.asgi:application