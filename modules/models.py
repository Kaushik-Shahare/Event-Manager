from modules import app

# Database 
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

db = SQLAlchemy(app)


# class name is table name
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(30), default='default')

    def __repr__(self) -> str:
        return f"{self.username} is Registered"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    long_description = db.Column(db.String(2000), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(80), nullable=False)
    organizer_name = db.Column(db.String(80), nullable=True)
    image_url = db.Column(db.String(200), nullable=False)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('events', lazy=True))

    def __repr__(self) -> str:
        return f"{self.title} is Organized by {self.organizer_name}"


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('registrations', lazy=True))
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

    def __repr__(self):
        return f"{self.user.username} has registered for {self.event}"


# initialize the database
with app.app_context():
    db.create_all()
