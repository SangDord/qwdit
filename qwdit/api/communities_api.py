from flask_restful import Resource, reqparse, abort
from flask_login import login_required
from flask import jsonify

from qwdit.models.users import User
from qwdit.models.community import Community
from qwdit import database


class CommunitiesResource(Resource):
    def get(self, community_id):
        session = database.create_session()
        community: Community = session.query(Community).get(community_id)
        if not community:
            abort(404, message=f'Community (id={community_id}) not found')
        return jsonify({'community': community.to_dict(only=('id', 'name', 'about', 'creator.username', 'created_at'))})


class CommunitiesListResource(Resource):
    def get(self):
        session = database.create_session()
        communities: list[Community] = session.query(Community).all()
        return jsonify({'communities': [item.to_dict(
            only=('id', 'name', 'about', 'creator_id', 'created_at')) for item in communities]})