# Import every model so SQLAlchemy can resolve relationship() targets by name.
from app.models.user import User  # noqa: F401
from app.models.place import Place, place_amenity  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.amenity import Amenity  # noqa: F401
