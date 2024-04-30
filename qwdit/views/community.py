from flask import (Blueprint, render_template, redirect, flash,
                   url_for, request, abort)
from flask_login import login_user, logout_user, current_user, login_required

from qwdit.forms import (SubmitTextForm, SubmitImgForm, CommunityCreateForm, EditCommunityProfileForm,
                         CommentCreateForm)
from qwdit import database

from qwdit.models.users import User
from qwdit.models.posts import Post, Community_post, Comment, PostScore
from qwdit.models.community import Community, Members
from qwdit import app

import os


bp = Blueprint('community', __name__)


@bp.route('/submit/text', methods=['GET', 'POST'])
@login_required
def submit_text():
    form = SubmitTextForm()
    if form.validate_on_submit():
        db_session = database.create_session()
        post = Post(
            author_id=current_user.id,
            title=form.title.data,
            body=form.text.data,
            category='text'
        )
        db_session.add(post)
        if form.community.data:
            community: Community = db_session.query(Community).filter(Community.name == form.community.data).first()
            community_post = Community_post(post.id, community.id)
            db_session.add(community_post)
        db_session.commit()
        return redirect('/')
    return render_template('community/submit_text.html', form=form)


@bp.route('/submit/img', methods=['GET', 'POST'])
@login_required
def submit_img():
    form = SubmitImgForm()
    if form.validate_on_submit():
        pass
    return render_template('community/submit_img.html', form=form)


@bp.route('/c/create', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CommunityCreateForm()
    if form.validate_on_submit():
        db_session = database.create_session()
        community = Community(name=form.name.data, creator_id=current_user.id)
        if form.about.data:
            community.about = form.about.data
        db_session.add(community)
        db_session.commit()
        return redirect(f'/c/{community.name}')
    return render_template('community/create.html', form=form)


@bp.route('/c/<string:community_name>/settings', methods=['GET', 'POST'])
@login_required
def community_settings(community_name):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    if not community:
        flash('That community does not exist', 'danger')
        return redirect('/home')
    if community.creator_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(f'/c/{community_name}')
    form = EditCommunityProfileForm()
    if form.validate_on_submit():
        if form.name.data != community.name:
            if db_session.query(Community).filter(Community.name == form.name.data,
                                                  Community.id != community.id).first():
                return render_template('/community/settings.html', form=form, community=community,
                                       message="That name is taken. Please choose a different name")
            if community.avatar != 'defaultcav.png':
                _, file_ext = os.path.splitext(community.avatar)
                avatar_fn = 'c-' + form.name.data + file_ext
                src = os.path.join(app.root_path, 'static/img/avatars', community.avatar)
                dst = os.path.join(app.root_path, 'static/img/avatars', avatar_fn)
                os.rename(src, dst)
                community.avatar = avatar_fn
            community.name = form.name.data
        if form.about.data != community.about:
            community.about = form.about.data
        if form.avatar.data:
            _, file_ext = os.path.splitext(form.avatar.data.filename)
            avatar_fn = 'c-' + community.name + file_ext
            avatar_path = os.path.join(app.root_path, 'static/img/avatars', avatar_fn)
            if community.avatar != 'defaultcav.png':
                os.remove(os.path.join(app.root_path, 'static/img/avatars', community.avatar))
            form.avatar.data.save(avatar_path)
            community.avatar = avatar_fn
        db_session.commit()
        flash('You have successfully updated community data', 'success')
        return redirect(f'/c/{community.name}')
    elif request.method == 'GET':
        form.name.data = community.name
        form.about.data = community.about
    return render_template('/community/settings.html', form=form, community=community)


@bp.route('/c/<string:community_name>/settings/reset_av')
@login_required
def reset_av(community_name):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    if not community:
        abort(404)
    if community.creator_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(f'/c/{community_name}')
    community.avatar = 'defaultcav.png'
    db_session.commit()
    flash("You have successfully reset community avatar", 'success')
    return redirect(f'/c/{community.name}')
    
    
@bp.route('/communities')
def communities_list():
    db_session = database.create_session()
    communities = db_session.query(Community).all()
    return render_template('community/community_list.html', communities=communities)
    
    
@bp.route('/c/<string:community_name>')
def community_profile(community_name):
    db_session = database.create_session()
    community = db_session.query(Community).filter(Community.name == community_name).first()
    if not community:
        abort(404)
    members = db_session.query(Members).filter(Members.community_id == community.id).count()
    return render_template('community/profile.html', community=community, members=members)


@bp.route('/c/<string:community_name>/join')
@login_required
def join(community_name):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    if not community:
        abort(404)
    community.join(current_user)
    return redirect(f'/c/{community_name}')


@bp.route('/c/<string:community_name>/leave')
@login_required
def leave(community_name):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    if not community:
        abort(404)
    community.leave(current_user)
    return redirect(f'/c/{community_name}')


@bp.route('/c/<string:community_name>/comments/<int:post_id>', methods=['GET', 'POST'])
def community_post_comments(community_name, post_id):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not community or not post:
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
    return render_template('community/comments.html', form=form, post=post)


def uprate_post(community_name, post_id):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not community or not post:
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


def downrate_post(community_name, post_id):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not community or not post:
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


@bp.route('/c/<string:community_name>/comments/<int:post_id>/uprate/comments')
@login_required
def uprate_post_comments(community_name, post_id):
    uprate_post(community_name, post_id)
    return redirect(f'/c/{community_name}/comments/{post_id}')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/downrate/comments')
@login_required
def downrate_post_comments(community_name, post_id):
    downrate_post(community_name, post_id)
    return redirect(f'/c/{community_name}/comments/{post_id}')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/uprate/home')
@login_required
def uprate_post_home(community_name, post_id):
    uprate_post(community_name, post_id)
    return redirect(f'/home')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/downrate/home')
@login_required
def downrate_post_home(community_name, post_id):
    downrate_post(community_name, post_id)
    return redirect('/home')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/uprate/user')
@login_required
def uprate_post_user(community_name, post_id):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not community or not post:
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
    return redirect(f'/user/{post.author.username}')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/downrate/user')
@login_required
def downrate_post_user(community_name, post_id):
    db_session = database.create_session()
    community: Community = db_session.query(Community).filter(Community.name == community_name).first()
    post: Post = db_session.query(Post).filter(Post.id == post_id).first()
    if not community or not post:
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
    return redirect(f'/user/{post.author.username}')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/uprate/community')
@login_required
def uprate_post_community(community_name, post_id):
    uprate_post(community_name, post_id)
    return redirect(f'/c/{community_name}')


@bp.route('/c/<string:community_name>/comments/<int:post_id>/downrate/community')
@login_required
def downrate_post_community(community_name, post_id):
    downrate_post(community_name, post_id)
    return redirect(f'/c/{community_name}')