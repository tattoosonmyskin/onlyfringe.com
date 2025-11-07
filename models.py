"""
Database models for OnlyFringe platform
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model for platform participants"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    arguments = db.relationship('Argument', backref='author', lazy=True)
    rebuttals = db.relationship('Rebuttal', backref='author', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Argument(db.Model):
    """Model for fact-based arguments"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Fact-checking status
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    ai_fact_check_result = db.Column(db.Text)
    
    # Relationships
    sources = db.relationship('Source', backref='argument', lazy=True, cascade='all, delete-orphan')
    rebuttals = db.relationship('Rebuttal', backref='argument', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_verified': self.is_verified,
            'verification_status': self.verification_status,
            'sources': [s.to_dict() for s in self.sources],
            'rebuttals': [r.to_dict() for r in self.rebuttals]
        }

class Source(db.Model):
    """Model for sources and references supporting arguments"""
    id = db.Column(db.Integer, primary_key=True)
    argument_id = db.Column(db.Integer, db.ForeignKey('argument.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'is_valid': self.is_valid
        }

class Rebuttal(db.Model):
    """Model for rebuttals to arguments"""
    id = db.Column(db.Integer, primary_key=True)
    argument_id = db.Column(db.Integer, db.ForeignKey('argument.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Fact-checking status
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(50), default='pending')
    ai_fact_check_result = db.Column(db.Text)
    
    # Relationships
    sources = db.relationship('RebuttalSource', backref='rebuttal', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_verified': self.is_verified,
            'verification_status': self.verification_status,
            'sources': [s.to_dict() for s in self.sources]
        }

class RebuttalSource(db.Model):
    """Model for sources supporting rebuttals"""
    id = db.Column(db.Integer, primary_key=True)
    rebuttal_id = db.Column(db.Integer, db.ForeignKey('rebuttal.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'is_valid': self.is_valid
        }
