from wtforms import (StringField, IntegerField, EmailField,
                     PasswordField, BooleanField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

from qwdit.database import create_session
from qwdit.models.users import User
from qwdit.models.community import Community

from re import fullmatch


REGS_MAIL_DOMAINS = ['com', 'org', 'ru']


def username_check(username):
    username_pattern = r"^[a-zA-Z0-9]+[a-zA-Z0-9_]+[a-zA-Z0-9]$"
    return fullmatch(username_pattern, username)


def email_check(email):
    email_pattern = rf"^[a-zA-Z0-9_.+-]+@[a-z-]+\.(?:{'|'.join(REGS_MAIL_DOMAINS)})+$"
    return fullmatch(email_pattern, email)


def communityname_check(communityname):
    communityname_pattern = r"^[a-zA-Z0-9]+[a-zA-Z0-9#()&$@?!\^|\\/;:\'\"\[\]\ _+-]+"
    return fullmatch(communityname_pattern, communityname)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    remember_me = BooleanField('Remember me')
    # recaptcha = RecaptchaField()
    submit = SubmitField('Log in')


class SignupForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    password_confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    agree = BooleanField()
    # recaptcha = RecaptchaField()
    submit = SubmitField('Sign up')
    
    def validate_username(self, username):
        session = create_session()
        if session.query(User).filter(User.username == username.data).first():
            raise ValidationError('That user name is taken. Please choose a different user name')
        if not username_check(username.data):
            raise ValidationError('That user name is incorrect. Please use only lowercase \
                and uppercase letters with numbers and underscores')
        if len(username.data) > 20:
                raise ValidationError('That user name is very long. Use less or equal to 20 characters')
    
    def validate_email(self, email):
        session = create_session()
        if session.query(User).filter(User.email == email.data).first():
            raise ValidationError('That email is taken. Please choose a different email')
        if not email_check(email.data):
            raise ValidationError(f'Email incorrect (use only: {", ".join(REGS_MAIL_DOMAINS)})')
        
    def validate_password(self, password):
        if len(password.data) > 60:
            raise ValidationError('That password is very long. Use less or equal to 60 characters')
    
    
class EditUserProfileForm(FlaskForm):
    avatar = FileField('Avatar', description="Allowed formats: .jpg, .png. Max size: 2mb",
                       validators=[FileAllowed(['jpg', 'png'])])
    username = StringField('User name', validators=[Length(min=3, max=20)])
    email = EmailField('Email', validators=[Email()])
    about = TextAreaField('About', validators=[Length(max=300)])
    password = PasswordField('Password')
    password_confirm = PasswordField('Confirm password', validators=[EqualTo('password')])
    submit = SubmitField('Edit')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            session = create_session()
            if session.query(User).filter(User.username == username.data).first():
                raise ValidationError('That user name is taken. Please choose a different user name')
            if not username_check(username.data):
                raise ValidationError('That user name is incorrect. Please use only lowercase \
                    and uppercase letters with numbers and underscores')
            if len(username.data) > 20:
                raise ValidationError('That user name is very long. Use less or equal to 20 characters')
            
    def validate_about(self, about):
        if len(about.data) > 300:
            raise ValidationError('About is very long. Use less or equal to 300 characters')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            session = create_session()
            if session.query(User).filter(User.email == email.data).first():
                raise ValidationError('That email is taken. Please choose a different email')
            if not email_check(email.data):
                raise ValidationError(f'Email incorrect (use only: {", ".join(REGS_MAIL_DOMAINS)})')
            
    def validate_password(self, password):
        if len(password.data) > 60:
            raise ValidationError('That password is very long. Use less or equal to 60 characters')


class SubmitTextForm(FlaskForm):
    community = StringField('Community')
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    text = TextAreaField('Text', validators=[DataRequired(), Length(min=5, max=2000)])
    submit = SubmitField('Submit')
    
    def validate_title(self, title):
        if len(title.data) > 100:
            raise ValidationError('That title is very long. Use less or equal to 100 characters')
        
    def validate_text(self, text):
        if len(text.data) > 2000:
            raise ValidationError('That title is very long. Use less or equal to 2000 characters')
        
    def validate_community(self, community):
        if community.data:
            db_session = create_session()
            if not db_session.query(Community).filter(Community.name == community.data).first():
                raise ValidationError('Community does not exist')
    
    
class SubmitImgForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=50)])
    img = FileField('Image', validators=[FileAllowed('jpg', 'png')])
    submit = SubmitField('Submit')
    
    
class CommunityCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    about = TextAreaField('About', validators=[Length(max=300)])
    submit = SubmitField('Submit')
    
    def validate_name(self, name):
        db_session = create_session()
        if db_session.query(Community).filter(Community.name == name.data).first():
            raise ValidationError('That name is taken. Please choose a different name')
        if not communityname_check(name.data):
            raise ValidationError('That name is incorrect. For first letter use only lowercase and \
                uppercase letters, numbers')
        if len(name.data) > 20:
            raise ValidationError('That name is very long. Use less or equal to 20 characters')
            
    def validate_about(self, about):
        if len(about.data) > 300:
            raise ValidationError('About is very long. Use less or equal to 300 characters')


class EditCommunityProfileForm(FlaskForm):
    pass