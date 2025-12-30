from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from flask_login import UserMixin

farm_crops = db.Table('farm_crops',
    db.Column('farm_id', db.Integer, db.ForeignKey('farm.id'), primary_key=True), 
    db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'), primary_key=True)
)

alert_blog_association = db.Table('alert_blog_association',
    db.Column('alert_id', db.Integer, db.ForeignKey('alert.id'), primary_key=True),
    db.Column('blog_post_id', db.Integer, db.ForeignKey('blog_post.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="farmer", server_default="farmer")
    settings = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_combined_settings(self):
        farm = Farm.query.filter_by(user_id=self.id).first()
        return {
            "farm_settings": farm.serialize() if farm else None,
            "general_settings": self.settings or {}
        }

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    temperature = db.Column(db.Float)  # Added for temperature tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Track updates
    
    crops = db.relationship('Crop', secondary=farm_crops, backref=db.backref('farms', lazy='dynamic'))
    alerts = db.relationship('Alert', backref='farm', lazy=True)  # Added relationship to alerts

    @property
    def primary_crop(self):
        return self.crops[0].name if self.crops else None

    def __repr__(self):
            return f'<Farm {self.location}>'

    def serialize(self):
        return {
            "location": self.location,
            "crops": [c.name for c in self.crops],
            "temperature": self.temperature,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def current_weather(self):
        return WeatherService.get_current_weather(self.location)
    
    def get_weather_forecast(self, days=3):
        return WeatherService.generate_forecast(self.location, days)

'''
class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('location', name='uq_weather_location'),
        db.Index('ix_weather_updated', 'last_updated')
    )
    
    farms = db.relationship('Farm', backref='weather_data', lazy=True)
    
    def serialize(self):
        return {
            "location": self.location,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "rainfall": self.rainfall,
            "wind_speed": self.wind_speed,
            "last_updated": self.last_updated.isoformat()
        }

    @classmethod
    def get_for_location(cls, location):
        return cls.query.filter_by(location=location).first() '''

class Alert(db.Model):  # Renamed from Prediction
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)  # Changed from user_id
    pest_name = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # low, medium, high
    type = db.Column(db.String(20), nullable=False)  # 'pest' or 'disease'
    description = db.Column(db.Text)
    recommended_actions = db.Column(db.JSON)  # Array of action strings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Added to manage alert status
    
    # Relationship to recommended articles
    recommended_posts = db.relationship('BlogPost', secondary='alert_blog_association', backref='alerts')
    def serialize(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "type": self.type,
            "pest_name": self.pest_name,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "description": self.description,
            "recommended_actions": self.recommended_actions or [],
            "recommended_posts": [post.serialize_minimal() for post in self.recommended_posts]
        }

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    recommended_model = db.Column(db.String(100))

    def __repr__(self):
        return f'<Crop {self.name}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.JSON)  # Store pest types as JSON array
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'

    def serialize_minimal(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.content[:100] + '...' if len(self.content) > 100 else self.content,
            "created_at": self.created_at.isoformat()
        }

class PestReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(50), nullable=False)
    pest_name = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    date_reported = db.Column(db.DateTime, default=db.func.current_timestamp())

class PredictionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(50), nullable=False)
    prediction = db.Column(db.String(200), nullable=False)
    date_predicted = db.Column(db.DateTime, default=db.func.current_timestamp())
