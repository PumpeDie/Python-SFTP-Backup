cd /usr/src/app
source /usr/src/app/venv/bin/activate
/usr/src/app/venv/bin/python3 /usr/src/app/src/archivage.py >> /var/log/cron.log 2>&1

