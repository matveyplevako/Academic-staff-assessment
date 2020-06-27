release: python mysite/manage.py migrate;python mysite/manage.py collectstatic --noinput
web: gunicorn -w 3 --chdir mysite mysite.wsgi --log-file -