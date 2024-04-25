from flask import (Blueprint, render_template, redirect, flash,
                   url_for, request, abort)
from flask_login import login_user, logout_user, current_user, login_required

from qwdit.forms import SubmitTextForm, SubmitImgForm, CommunityCreateForm
from qwdit import database

from qwdit.models.users import User
from qwdit.models.posts import Post
from qwdit.models.community import Community


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
        if len(form.name.data) > 32:
            return render_template('community/create.html', form=form,
                                   message="Name is too long. Use less or equal to 32")
        if db_session.query(Community).filter(Community.name == form.name.data).first():
            return render_template('community/create.html', form=form,
                                   message="Community with this name is already exist")
        community = Community(name=form.name.data, creator_id=current_user.id)
        if form.about.data:
            community.about = form.about.data
        db_session.add(community)
        db_session.commit()
        return redirect(f'/c/{community.name}')
    return render_template('community/create.html', form=form)


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
    return render_template('community/profile', community=community)


@bp.route('/c/<string:community_name>/comments/<int:post_id>')
def posts_comments(community_name, post_id):
    pass


@bp.route('/c/<string:community_name>/comments/<int:post_id>/<int:comment_id>')
def posts_comment(community_name, post_id, comment_id):
    pass