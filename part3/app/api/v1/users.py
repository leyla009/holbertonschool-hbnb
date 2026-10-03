from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
})


def serialize_user(user):
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered or invalid input data')
    def post(self):
        """Register a new user"""
        try:
            new_user = facade.create_user(api.payload)
        except ValueError as e:
            return {'error': str(e)}, 400
        return {'id': new_user.id, 'message': 'User successfully created'}, 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of all users"""
        return [serialize_user(u) for u in facade.get_all_users()], 200


@api.route('/<string:user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return serialize_user(user), 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, user_id):
        """Update your own user information (not email or password)"""
        if user_id != get_jwt_identity():
            return {'error': 'Unauthorized action'}, 403
        payload = api.payload
        if 'email' in payload or 'password' in payload:
            return {'error': 'You cannot modify email or password'}, 400
        data = {k: payload[k] for k in ('first_name', 'last_name') if k in payload}
        try:
            user = facade.update_user(user_id, data)
        except ValueError as e:
            return {'error': str(e)}, 400
        if not user:
            return {'error': 'User not found'}, 404
        return serialize_user(user), 200