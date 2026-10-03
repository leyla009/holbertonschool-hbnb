from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1.utils import current_user_is_admin
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place'),
})

review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
})


def serialize_review(review):
    return {
        'id': review.id,
        'text': review.text,
        'rating': review.rating,
        'user_id': review.user_id,
        'place_id': review.place_id,
    }


def serialize_review_summary(review):
    return {'id': review.id, 'text': review.text, 'rating': review.rating}


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new review (the author is the authenticated user)"""
        review_data = dict(api.payload)
        review_data['user_id'] = get_jwt_identity()
        try:
            review = facade.create_review(review_data)
        except ValueError as e:
            return {'error': str(e)}, 400
        return serialize_review(review), 201

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        return [serialize_review_summary(r) for r in facade.get_all_reviews()], 200


@api.route('/<string:review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return serialize_review(review), 200

    @api.expect(review_update_model, validate=True)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, review_id):
        """Update a review (author or admin)"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not current_user_is_admin() and review.user_id != get_jwt_identity():
            return {'error': 'Unauthorized action'}, 403
        try:
            facade.update_review(review_id, api.payload)
        except ValueError as e:
            return {'error': str(e)}, 400
        return {'message': 'Review updated successfully'}, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review (author or admin)"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not current_user_is_admin() and review.user_id != get_jwt_identity():
            return {'error': 'Unauthorized action'}, 403
        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200
