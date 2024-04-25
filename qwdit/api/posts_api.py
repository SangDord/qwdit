from flask_restful import Resource, reqparse, abort
from flask_login import login_required, current_user
from flask import jsonify

from qwdit.models.users import User
from qwdit.models.posts import Post, Community_post
from qwdit.models.community import Community
from qwdit import database

post_create_parser = reqparse.RequestParser()
post_create_parser.add_argument('title', required=True)
post_create_parser.add_argument('body', required=True)
post_create_parser.add_argument('category', choices=('text', 'image', 'link'), default='text')
post_create_parser.add_argument('community', default='')
        
        
class PostsResource(Resource):
    def get(self, post_id):
        session = database.create_session()
        post: Post = session.query(Post).get(post_id)
        if not post:
            abort(404, message=f'Post (id={post_id}) not found')
            

class PostsListResource(Resource):
    def get(self):
        session = database.create_session()
        posts: list[Post] = session.query(Post).all()
        return jsonify({'posts': [item.to_dict(only=('title', 'body', 'author.username',
                                                     'created_at')) for item in posts]})
        
    @login_required
    def post(self):
        args = post_create_parser.parse_args()
        session = database.create_session()
        if args.community:
            community: Community = session.query(Community).filter(Community.name == args.community)
            if not community:
                abort('404', message=f'Community ({args.community}) not found')
        post = Post(
            title=args.title,
            body=args.body,
            user_id=current_user.id,
            category=args.category
        )
        if args.community:
            Community_post(
                community_id=community.id,
                post_id=post.id
            )
        return jsonify({'title': post.title, 'success': 'ok'})


class PostCommentsListResource(Resource):
    def get(self, post_id):
        pass
    
    def post(self, post_id):
        pass
    

class PostCommentsResource(Resource):
    def get(self, comment_id):
        pass
    
    @login_required
    def put(self, comment_id):
        pass
    
    @login_required
    def delete(self, comment_id):
        pass