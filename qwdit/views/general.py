from flask import (Blueprint, render_template, redirect, flash,
                   url_for, request, abort)
from flask_login import login_user, logout_user, current_user, login_required

from qwdit.forms import LoginForm, SignupForm, EditUserProfileForm, CommentCreateForm
from qwdit import database
from qwdit.models.users import User, Followers
from qwdit.models.posts import Post, PostScore, Comment
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


@bp.route('/users')
def user_list():
    db_session = database.create_session()
    users: list[User] = db_session.query(User).all()
    return render_template('general/user_list.html', users=users)


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
    followers = db_session.query(Followers).filter(Followers.followed_id == user.id).count()
    following = db_session.query(Followers).filter(Followers.follower_id == user.id).count()
    return render_template('general/profile.html', user=user, followers=followers, following=following)


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


@bp.route('/user/<string:username>/follow')
@login_required
def follow(username):
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.username == username).first()
    if not user:
        abort(404)
    if user == current_user:
        abort(400)
    user.follow(current_user)
    return redirect(f'/user/{username}')


@bp.route('/user/<string:username>/unfollow')
@login_required
def unfollow(username):
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.username == username).first()
    if not user:
        abort(404)
    if user == current_user:
        abort(400)
    user.unfollow(current_user)
    return redirect(f'/user/{username}')


@bp.route('/user/<string:username>/comments/<int:post_id>', methods=['GET', 'POST'])
def user_post_comments(username, post_id):
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.username == username).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not user or not post:
        abort(404)
    form = CommentCreateForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            abort(401)
        comment = Comment(post_id=post.id,
                          user_id=current_user.id,
                          body=form.body.data)
        db_session.add(comment)
        db_session.commit()
    return render_template('general/comments.html', form=form, post=post)


def uprate_post(username, post_id):
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.username == username).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not user or not post:
        abort(404)
    flag = None
    for score in post.scores:
        if score.user == current_user:
            flag = score.liked
            if score.liked is True:
                db_session.delete(score)
            elif score.liked is False:
                score.liked = True
            break
    if flag is None:
        score = PostScore(user_id=current_user.id,
                          post_id=post_id,
                          liked=True)
        db_session.add(score)
    db_session.commit()


def downrate_post(username, post_id):
    db_session = database.create_session()
    user: User = db_session.query(User).filter(User.username == username).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not user or not post:
        abort(404)
    flag = None
    for score in post.scores:
        if score.user == current_user:
            flag = score.liked
            if score.liked is False:
                db_session.delete(score)
            elif score.liked is True:
                score.liked = False
            break
    if flag is None:
        score = PostScore(user_id=current_user.id,
                          post_id=post_id,
                          liked=False)
        db_session.add(score)
    db_session.commit()


@app.route('/user/<string:username>/comments/<int:post_id>/uprate/home')
@login_required
def uprate_post_home(username, post_id):
    uprate_post(username, post_id)
    return redirect('/home')


@app.route('/user/<string:username>/comments/<int:post_id>/downrate/home')
@login_required
def downrate_post_home(username, post_id):
    downrate_post(username, post_id)
    return redirect('/home')


@app.route('/user/<string:username>/comments/<int:post_id>/uprate/user')
def uprate_post_user(username, post_id):
    uprate_post(username, post_id)
    return redirect(f'/user/{username}')


@app.route('/user/<string:username>/comments/<int:post_id>/downrate/user')
def downrate_post_user(username, post_id):
    downrate_post(username, post_id)
    return redirect(f'/user/{username}')