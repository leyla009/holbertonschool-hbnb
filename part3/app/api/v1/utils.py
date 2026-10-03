from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def current_user_is_admin():
    """True if the (already verified) JWT carries is_admin = True."""
    return bool(get_jwt().get('is_admin', False))


def admin_required(fn):
    """Require a valid JWT whose is_admin claim is True (401 / 403 otherwise)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if not current_user_is_admin():
            return {'error': 'Admin privileges required'}, 403
        return fn(*args, **kwargs)
    return wrapper
