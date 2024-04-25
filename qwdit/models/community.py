import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from datetime import datetime

from qwdit.database import SqlAlchemyBase


class Community(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'communities'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100))
    creator_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    
    creator = relationship('User')
    created_post = relationship('Community_post', back_populates='community')
    
    def __init__(self, name, creator_id):
        self.name = name
        self.creator = creator_id


class Community_follows(SqlAlchemyBase):
    __tablename__ = 'community_follows'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    community_id = sa.Column(sa.Integer, sa.ForeignKey('communities.id'))
    member_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))