from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This will be initialized in setup_database.py
db = SQLAlchemy()

class User(db.Model):
    """User model representing a user in the system"""
    __tablename__ = 'users'
    
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False)
    
    # Relationship: One user can have many items
    items = db.relationship('Item', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Item(db.Model):
    """Item model representing a todo item"""
    __tablename__ = 'items'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.String)
    
    # Foreign key: Each item belongs to a user
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Convert item to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'timestamp': self.timestamp,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Item {self.id}: {self.title}>'
