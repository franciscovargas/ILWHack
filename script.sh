rm project/server/dev.sqlite
rm -rf migrations
python manage.py create_db
python manage.py db init
python manage.py db migrate
python manage.py create_admin
python manage.py create_data
