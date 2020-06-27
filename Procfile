release: python mysite/manage.py migrate
web: python mysite/manage.py collectstatic --noinput && gunicorn -w 1 --chdir mysite mysite.wsgi --log-file -