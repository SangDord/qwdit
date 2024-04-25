from flask import Flask, render_template
from flask_login import LoginManager
from flask_restful import Api

from qwdit import database
import os

app = Flask(__name__)
app.config.from_pyfile(os.environ.get('QWDIT_CONFIG'))

database.global_init(app)

login_manager = LoginManager()
login_manager.init_app(app)

from qwdit.api import users_api, posts_api, communities_api

api = Api(app)
api.add_resource(users_api.UsersResource, '/api/users/<string:username>')
api.add_resource(users_api.UsersListResource, '/api/users')
api.add_resource(users_api.UserLoginResource, '/api/login')
api.add_resource(users_api.UserSignupResource, '/api/signup')
api.add_resource(users_api.UserLogoutResource, '/api/logout')

api.add_resource(posts_api.PostsResource, '/api/posts/<int:post_id>')
api.add_resource(posts_api.PostsListResource, '/api/posts')

api.add_resource(communities_api.CommunitiesResource, '/api/communities/<int:community_id>')
api.add_resource(communities_api.CommunitiesListResource, '/api/communities')

from qwdit.models.users import User

@login_manager.user_loader
def load_user(user_id):
    session = database.create_session()
    return session.query(User).get(user_id)

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

from qwdit.views import general
app.register_blueprint(general.bp)