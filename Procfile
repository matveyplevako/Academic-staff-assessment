release: python mysite/manage.py migrate
web: gunicorn -w 3 --chdir mysite mysite.wsgi --log-file -