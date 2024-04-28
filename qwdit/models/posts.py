import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime

from sqlalchemy_serializer import SerializerMixin

from qwdit.database import SqlAlchemyBase


class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    title = sa.Column(sa.String(100))
    body = sa.Column(sa.String)
    category = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    author = relationship('User')
    community_post = relationship('Community_post', back_populates='post')
    
    def __init__(self, author_id, title, body, category):
        self.author_id = author_id
        self.title = title
        self.body = body
        self.category = category

        
class Community_post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'community_posts'
    
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'), primary_key=True)
    community_id = sa.Column(sa.Integer, sa.ForeignKey('communities.id'))
    
    post = relationship('Post')
    community = relationship('Community')
    
    def __init__(self, post_id, community_id):
        self.post_id = post_id
        self.community_id = community_id
        

class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    body = sa.Column(sa.String)
    
    def __init__(self, post_id, user_id):
        self.post_id = post_id
        self.user_id = user_id
    
    
class PostScore(SqlAlchemyBase):
    __tablename__ = 'post_scores'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))
    liked = sa.Column(sa.Boolean)
    

class CommentScore(SqlAlchemyBase):
    __tablename__ = 'comment_scores'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    comment_id = sa.Column(sa.Integer, sa.ForeignKey('comments.id'))
    liked = sa.Column(sa.Boolean)