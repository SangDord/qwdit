import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from qwdit.database import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(20))
    email = sa.Column(sa.String)
    about = sa.Column(sa.String(300), default='')
    avatar = sa.Column(sa.String, default='defaultuav.png')
    hashed_password = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    created_communities = relationship('Community', back_populates='creator')
    created_posts = relationship('Post', back_populates='author')
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    @property
    def is_admin(self):
        pass


class User_follows(SqlAlchemyBase):
    __tablename__ = 'user_follows'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    following_user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    followed_user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    
    def __init__(self, flg, fld):
        self.following_user_id = flg
        self.followed_user_id = fld