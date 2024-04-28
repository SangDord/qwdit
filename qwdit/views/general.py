from flask import (Blueprint, render_template, redirect, flash,
                   url_for, request, abort)
from flask_login import login_user, logout_user, current_user, login_required

from qwdit.forms import LoginForm, SignupForm, EditUserProfileForm
from qwdit import database
from qwdit.models.users import User
from qwdit.models.posts import Post
from qwdit import app

import os


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
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    form = LoginForm()
    if form.validate_on_submit():
        db_session = database.create_session()
        user: User = db_session.query(User).filter(User.email == form.email.data).first()
        if not user:
            flash('Wrong email. User not found', 'danger')
            return render_template('general/login.html', form=form, message="Wrong email. User not found")
        if not user.verify_password(form.password.data):
            flash('Wrong password. Please check email or password', 'danger')
            return render_template('general/login.html', form=form, message="Wrong password")
        login_user(user, remember=form.remember_me.data)
        flash('You have successfully logged in', 'success')
        return redirect('/')
    return render_template('general/login.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    form = SignupForm()
    if form.validate_on_submit():
        db_session = database.create_session()
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db_session.add(user)
        db_session.commit()
        flash('You have successfully signed up', 'success')
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


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = EditUserProfileForm()
    if form.validate_on_submit():
        db_session = database.create_session()
        user: User = db_session.query(User).filter(User.email == current_user.email).first()
        if form.username.data != user.username:
            if user.avatar != 'defaultuav.png':
                _, file_ext = os.path.splitext(user.avatar)
                avatar_fn = 'u-' + form.username.data + file_ext
                src = os.path.join(app.root_path, 'static/img/avatars', user.avatar)
                dst = os.path.join(app.root_path, 'static/img/avatars', avatar_fn)
                os.rename(src, dst)
                user.avatar = avatar_fn
            user.username = form.username.data
        if form.email.data != user.email:
            user.email = form.email.data
        if form.about.data != user.about:
            user.about = form.about.data
        if form.password.data and not user.verify_password(form.password.data):
            user.set_password(form.password.data)
        if form.avatar.data:
            _, file_ext = os.path.splitext(form.avatar.data.filename)
            avatar_fn = 'u-' + user.username + file_ext
            avatar_path = os.path.join(app.root_path, 'static/img/avatars', avatar_fn)
            if user.avatar != 'defaultuav.png':
                os.remove(os.path.join(app.root_path, 'static/img/avatars', user.avatar))
            form.avatar.data.save(avatar_path)
            user.avatar = avatar_fn
        db_session.commit()
        flash('You have successfully updated profile data', 'success')
        return redirect('/account')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about.data = current_user.about
        form.email.data = current_user.email
    return render_template('/general/settings.html', form=form)


@bp.route('/settings/reset_av')
@login_required
def reset_av():
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.email == current_user.email).first()
    user.avatar = 'defaultuav.png'
    db_session.commit()
    flash('You have successfully reset avatar', 'success')
    return redirect('/account')