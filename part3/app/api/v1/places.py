from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1.utils import current_user_is_admin
from app.services import facade

api = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place (the owner is the authenticated user)"""
        place_data = dict(api.payload)
        place_data['owner_id'] = get_jwt_identity()
        try:
            new_place = facade.create_place(place_data)
        except (ValueError, KeyError) as e:
            return {'error': str(e)}, 400
        return {'id': new_place.id, 'title': new_place.title,
                'description': new_place.description, 'price': new_place.price,
                'latitude': new_place.latitude, 'longitude': new_place.longitude,
                'owner_id': new_place.owner_id}, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        return [{'id': p.id, 'title': p.title, 'price': p.price,
                 'latitude': p.latitude, 'longitude': p.longitude}
                for p in places], 200


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        owner = place.owner
        return {'id': place.id, 'title': place.title,
                'description': place.description, 'price': place.price,
                'latitude': place.latitude, 'longitude': place.longitude,
                'owner': {'id': owner.id,
                          'first_name': owner.first_name,
                          'last_name': owner.last_name,
                          'email': owner.email},
                'amenities': [{'id': a.id, 'name': a.name} for a in place.amenities],
                'reviews': [{'id': r.id, 'text': r.text, 'rating': r.rating,
                             'user_id': r.user_id,
                             'user_name': f'{r.user.first_name} {r.user.last_name}'}
                            for r in place.reviews]}, 200

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, place_id):
        """Update a place's information (owner or admin)"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if not current_user_is_admin() and place.owner_id != get_jwt_identity():
            return {'error': 'Unauthorized action'}, 403
        try:
            facade.update_place(place_id, api.payload)
        except ValueError as e:
            return {'error': str(e)}, 400
        return {'message': 'Place updated successfully'}, 200

    @api.response(200, 'Place deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @jwt_required()
    def delete(self, place_id):
        """Delete a place (owner or admin)"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if not current_user_is_admin() and place.owner_id != get_jwt_identity():
            return {'error': 'Unauthorized action'}, 403
        facade.delete_place(place_id)
        return {'message': 'Place deleted successfully'}, 200


@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        reviews = facade.get_reviews_by_place(place_id)
        if reviews is None:
            return {'error': 'Place not found'}, 404
        return [{'id': r.id, 'text': r.text, 'rating': r.rating} for r in reviews], 200