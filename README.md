# Vita's app

#### Video Demo: https://youtu.be/iUF180hIDa0

#### Description:

final project for CS50 course

My Project is a simple application that allows
user to write down notes and other information and
allows them to share it with one selected person.

The app is genereted by Flask and it is using many
useful extensions - for example SQLAlchemy to work
with a database, WTForms for form validation,
FLask-login to keep track if user is autenticaited.
All extensions are listed in file requirements.txt

content:
app - main folder, contains another folders, app init file, forms.py, models.py (db SETUP), errors.py, etc.
app/routes.py - serve all the routes for app
app/static - contains icons, images and script.js
app/templates - contains HTML file made with jinja template language
requirements.txt - contains all extensions used in this app, extensions can be instaled with command:
pip install -r requirements.txt

after installation to run an app use command:
flask run
