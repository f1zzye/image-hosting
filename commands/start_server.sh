#!/bin/bash

mkdir -p /image-hosting/src/static
mkdir -p /image-hosting/src/media
mkdir -p /image-hosting/src/staticfiles

python src/manage.py makemigrations
python src/manage.py migrate

python src/manage.py collectstatic --noinput --clear

python src/manage.py runserver 0.0.0.0:8000