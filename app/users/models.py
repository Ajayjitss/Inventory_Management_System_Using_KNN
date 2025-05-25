from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint

class User(db.Model, UserMixin):
    """
    User model: Represents the users of the application.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20))  # Role-based access control

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set a hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if a given password matches the stored password."""
        return check_password_hash(self.password, password)
