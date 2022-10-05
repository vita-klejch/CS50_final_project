from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class newConnectionForm(FlaskForm):
    user_to_connect = StringField('e-mail', validators=[DataRequired()])
    submit = SubmitField('Connect with user')

class NewNoticeForm(FlaskForm):
    text = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create New Notice')

class NewItemForm(FlaskForm):
    text = StringField('Item title', validators=[DataRequired()])
    submit = SubmitField('Add Item')

class ChangeNoticeForm(FlaskForm):
    text = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Change Title')

class ChangeTaskForm(FlaskForm):
    text = StringField('Item title', validators=[DataRequired()])
    submit = SubmitField('Change Item')


