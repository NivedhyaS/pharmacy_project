web: python manage.py migrate --noinput && python create_admin.py && python manage.py collectstatic --noinput && gunicorn pharmacy.wsgi --log-file -
