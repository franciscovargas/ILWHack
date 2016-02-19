# ILW Hack 2016 (Team Banitsa)

This app was designed  with the intention of being a prototype recomender system
for dixons carphone. The app is flask based and used the standard python
data science modules and should be installable via:

    $ pip install -r requirements.txt

We also built a wrapper around the revoo API nonetheless due to privacy proetection
issues the app was trialled partially with fake data.

After a succesfull installation run the project with the following commands:

     $ chmod a+x script.sh
     $ ./script.sh  # database migrations and set up
     $ python manage.py create_data_u
     $ python manage.py create_data_pur
     $ export APP_SETTINGS="project.server.config.DevelopmentConfig"
     $ python manage.py runserver

