#!/bin/sh

while ! pg_isready -U postgres -h db
do
echo "$(date) - waiting for database to start"
    sleep 2
done

python spinnaker/spinnaker.py db upgrade
uwsgi --ini uwsgi.ini
