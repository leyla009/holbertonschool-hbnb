from flask_sqlalchemy import SQLAlchemy

# Shared database object. It lives in its own module so that both the
# application factory and the persistence layer can import it without a
# circular import.
db = SQLAlchemy()