from flask_restful import Resource, reqparse, abort
from flask_login import login_required
from flask import jsonify

from qwdit.models.users import User
from qwdit import database


class CommunitiesResource(Resource):
    pass


class CommunitiesListResource(Resource):
    pass