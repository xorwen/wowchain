#!/bin/bash
export FLASK_APP="api.py"
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
gunicorn --workers 3 --bind 0.0.0.0:80  wsgi:app