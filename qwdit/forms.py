from wtforms import (StringField, IntegerField, EmailField,
                     PasswordField, BooleanField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # recaptcha = RecaptchaField()
    submit = SubmitField('Log in')
    

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm password', validators=[DataRequired()])
    agree = BooleanField()
    # recaptcha = RecaptchaField()
    submit = SubmitField('Sign up')
    
    
class EditUserProfileForm(FlaskForm):
    pass


class SubmitTextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    
class SubmitImgForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    img = FileField('Image', validators=[FileAllowed('jpg', 'png')])
    submit = SubmitField('Submit')
    
    
class CommunityCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About')
    submit = SubmitField('Submit')
    
    
class EditCommunityProfileForm(FlaskForm):
    pass