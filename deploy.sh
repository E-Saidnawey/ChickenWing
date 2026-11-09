#!/bin/sh
# Usage: ./deploy.sh user@your-server-ip
set -e
python3 build.py
rsync -avz --delete public/ "$1":/var/www/site/
