from flask import (Blueprint, render_template, redirect, flash,
                   url_for, request, abort)
from flask_login import login_user, logout_user, current_user, login_required
from qwdit.forms import LoginForm, SignupForm, SubmitTextForm, SubmitImgForm
from qwdit import database
from qwdit.models.users import User
from qwdit.models.posts import Post
import requests

bp = Blueprint('general', __name__)

@bp.route('/')
def index():
    return redirect('/home')

@bp.route('/home')
def home():
    db_session = database.create_session()
    posts: list[Post] = db_session.query(Post).all()
    return render_template('general/home.html', posts=posts)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_session = database.create_session()
        user: User = db_session.query(User).filter(User.email == form.email.data).first()
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
    return redirect('/')
    

@bp.route('/account')
@login_required
def account():
    return redirect('/user/' + current_user.username)


@bp.route('/user/<string:username>')
def profile(username):
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.username == username).first()
    if not user:
        abort(404)
    return render_template('general/profile.html', user=user)
