import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from datetime import datetime

from qwdit.database import SqlAlchemyBase, create_session


class Members(SqlAlchemyBase):
    __tablename__ = 'members'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    member_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    community_id = sa.Column(sa.Integer, sa.ForeignKey('communities.id'))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    
    def __init__(self, member_id, community_id):
        self.member_id = member_id
        self.community_id = community_id


class Community(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'communities'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(20))
    about = sa.Column(sa.String(300), default='')
    avatar = sa.Column(sa.String, default='defaultcav.png')
    creator_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    creator = relationship('User')
    created_posts = relationship('Community_post', back_populates='community')
    
    members = relationship('User', secondary='members', backref='community_id')
    
    def is_joined(self, user):
        session = create_session()
        return session.query(Members).filter(Members.member_id == user.id,
                                         Members.community_id == self.id).count() > 0
    
    def join(self, user):
        if not self.is_joined(user):
            session = create_session()
            session.add(Members(member_id=user.id, community_id=self.id))
            session.commit()
    
    def leave(self, user):
        if self.is_joined(user):
            session = create_session()
            members = session.query(Members).filter(Members.member_id == user.id,
                                                    Members.community_id == self.id).first()
            session.delete(members)
            session.commit()
    
    def __init__(self, name, creator_id):
        self.name = name
        self.creator_id = creator_id