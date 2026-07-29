"""SQLAlchemy and Flask-Migrate extension instances.

Import `db` and `migrate` from here rather than instantiating them
inside individual modules to avoid circular imports.

Usage
-----
    from database.db import db, migrate

    # In the application factory:
    db.init_app(app)
    migrate.init_app(app, db)
"""
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
