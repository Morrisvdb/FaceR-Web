from __init__ import app, db

class Contestant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    
    objects = db.relationship('FoundObjects', backref='contestant', lazy=True, cascade='all, delete-orphan')

class FoundObjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(32), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    contestant_id = db.Column(db.Integer, db.ForeignKey('contestant.id'), nullable=False)
    
with app.app_context():
    db.create_all()