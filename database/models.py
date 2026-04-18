from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, Any
import uuid

# This will be initialized in setup_database.py
db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship: One user can have many items
    items = db.relationship('Item', backref='user', lazy='dynamic', 
                            cascade='all, delete-orphan', passive_deletes=True)
    
    def to_dict(self) -> Dict[str, Any]:

        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'

class Item(db.Model):

    __tablename__ = 'items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: uuid.uuid4())
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="ToDo")
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), 
                    nullable=False, index=True)
    
    __table_args__ = (
        db.CheckConstraint(status.in_(["ToDo", "InProgress", "Done"]),
                           name="valid_status_check"),
    )

    def to_dict(self):

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id
        }
    
    def __repr__(self) -> str:
        return f'<Item {self.id}: {self.title}>'
