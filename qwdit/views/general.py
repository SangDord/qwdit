from flask import (Blueprint, render_template, redirect, flash,
                   url_for, request)
from flask_login import login_user, logout_user, current_user, login_required

from qwdit.forms import LoginForm, SignupForm, SubmitTextForm, SubmitImgForm
from qwdit import database
from qwdit.models.users import User
from qwdit.models.posts import Post
import requests

bp = Blueprint('general', __name__)

@bp.route('/')
def index():
    return render_template('general/index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = database.create_session()
        user: User = session.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template('general/login.html', form=form, message="Wrong email. User not found")
        if not user.verify_password(form.password.data):
            return render_template('general/login.html', form=form, message="Wrong password")
        login_user(user)
        return redirect('/')
    return render_template('general/login.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if form.password.data != form.password_confirm.data:
            return render_template('general/signup.html', form=form, message="Passwords don't match")
        data = {
            "email": form.email.data,
            "password": form.password.data,
            "username": form.username.data
        }
        resp = requests.post(f'{request.url_root}/api/signup', json=data).json()
        if resp['signup_code'] in [1, 2, 3]:
            return render_template('general/signup.html', form=form, message=resp['message'])
        return redirect('/login')
    return render_template('general/signup.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    redirect('/')
    

@bp.route('/submit/text')
@login_required
def submit_text():
    form = SubmitTextForm()
    if form.validate_on_submit():
        pass
    return render_template('general/submit_text.html', form=form)


@bp.route('/submit/img')
@login_required
def submit_img():
    form = SubmitImgForm()
    if form.validate_on_submit():
        pass
    return render_template('general/submit_img.html', form=form)