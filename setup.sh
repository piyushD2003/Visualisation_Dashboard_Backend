#!/bin/bash

# install dependencies
pip install -r requirements.txt

# apply migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# collect static files for Vercel to serve
python manage.py collectstatic --noinput
