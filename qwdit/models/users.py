import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from qwdit.database import SqlAlchemyBase, create_session


class Followers(SqlAlchemyBase):
    __tablename__ = 'followers'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    follower_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    followed_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    
    def __init__(self, flr, fld):
        self.follower_id = flr
        self.followed_id = fld


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
    created_comments = relationship('Comment', back_populates='author')
    
    followed = relationship('User', secondary='followers',
                            primaryjoin=(Followers.follower_id == id),
                            secondaryjoin=(Followers.followed_id == id),
                            backref="followed_id")
    
    
    def is_following(self, user):
        session = create_session()
        return session.query(Followers).filter(Followers.followed_id == self.id,
                                               Followers.follower_id == user.id).count() > 0
    
    def follow(self, user):
        if not self.is_following(user):
            session = create_session()
            session.add(Followers(user.id, self.id))
            session.commit()
    
    def unfollow(self, user):
        if self.is_following(user):
            session = create_session()
            followers = session.query(Followers).filter(Followers.followed_id == self.id,
                                                        Followers.follower_id == user.id).first()
            session.delete(followers)
            session.commit()
            
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


