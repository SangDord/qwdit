from flask_restful import Resource, reqparse, abort
from flask_login import login_required, login_user, current_user, logout_user
from flask import jsonify

from qwdit.models.users import User
from qwdit import database

from re import fullmatch

REGS_MAIL_DOMAINS = ['com', 'org', 'ru']

signup_parser = reqparse.RequestParser()
signup_parser.add_argument('username', required=True)
signup_parser.add_argument('email', required=True)
signup_parser.add_argument('password', required=True)

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', required=True)
login_parser.add_argument('password', required=True)


def email_check(email):
    email_pattern = rf"^[a-zA-Z0-9_.+-]+@[a-z-]+\.(?:{'|'.join(REGS_MAIL_DOMAINS)})+$"
    return fullmatch(email_pattern, email)


class UsersResource(Resource):
    def get(self, username):
        session = database.create_session()
        user: User = session.query(User).filter(User.username == username).first()
        if not user:
            abort(404, message=f'User ({username}) not found')
        return jsonify({'user': [user.to_dict(only=({'username', 'email', 'about'}))]})
    
    @login_required
    def put(self, username):
        session = database.create_session()
        user: User = session.query(User).filter(User.username == username).first()
        if not user:
            abort(404, message=f'User ({username}) not found')
    
    @login_required
    def delete(self, username):
        session = database.create_session()
        user: User = session.query(User).filter(User.username == username).first()
        if not user:
            abort(404, message=f'User ({username}) not found')
        if current_user.id != user.id:
            abort(403, message='Access denied')
        session.delete(user)
        session.commit()
        return jsonify({'username': username, 'success': True})
    

class UsersListResource(Resource):
    def get(self):
        session = database.create_session()
        users: list[User] = session.query(User).all()
        return jsonify({'users': [item.to_dict(only=('username', 'email')) for item in users]})


class UserLoginResource(Resource):
    def post(self):
        args = login_parser.parse_args()
        session = database.create_session()
        user: User = session.query(User).filter(User.email == args.email).first()
        if not user:
            abort(404, message='Wrong email. User not found', login_code=1)
        if not user.verify_password(args.password):
            abort(400, message='Wrong password', login_code=2)
        login_user(user)
        return jsonify({'message': 'Successful log in', 'login_code': 0})


class UserSignupResource(Resource):
    def post(self):
        args = signup_parser.parse_args()
        session = database.create_session()
        if session.query(User).filter(User.email == args.email).first():
            abort(409, message='Email is already busy', signup_code=1)
        if session.query(User).filter(User.username == args.username).first():
            abort(409, message='Username is already busy', signup_code=2)
        if not email_check(args.email):
            abort(400, message=f'Email incorrect. Use only: {",".join(REGS_MAIL_DOMAINS)}', signup_code=3)

        user = User(
            username=args.username,
            email=args.email,
            password=args.password
        )
        
        session.add(user)
        session.commit()
        return jsonify({'message': 'Successful sign up', 'signup_code': 0})
    
    
class UserLogoutResource(Resource):
    @login_required
    def get(self):
        logout_user()
        return jsonify({'message': 'Successful log out', 'logout_code': 0})