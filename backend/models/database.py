"""
Database initialisation module.
Creates and exports the shared SQLAlchemy instance used by all models.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy instance -- imported by every model module
db = SQLAlchemy()


def init_db(app):
    """
    Bind the SQLAlchemy instance to the Flask application and create all
    tables that do not yet exist.

    Args:
        app: The Flask application instance.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
