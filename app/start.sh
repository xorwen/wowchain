#!/bin/bash
gunicorn --workers 3 --bind 0.0.0.0:80  wsgi:app