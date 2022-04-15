from flask_login import UserMixin
from .database import db 
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    trackers = db.relationship("Tracker")

class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    type = db.Column(db.String) # db.CheckConstraint('"type" = "Num" OR "Mul" OR "Time" OR "Bool"')
    mcb = db.Column(db.String) #mcb - multiple choice or boolean
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
class Data(db.Model):
    __tablename__ = 'data'
    did = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    tracker_id = db.Column(db.Integer,  db.ForeignKey("tracker.id"))
    value = db.Column(db.String)
    note = db.Column(db.String)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = func.now())