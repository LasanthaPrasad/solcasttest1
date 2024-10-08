from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    grid_substation = db.Column(db.String(100))
    feeder_number = db.Column(db.String(50))
    forecasts = db.relationship('Forecast', backref='location', lazy=True)

class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    ghi = db.Column(db.Float)
    ghi90 = db.Column(db.Float)
    ghi10 = db.Column(db.Float)
    ebh = db.Column(db.Float)
    dni = db.Column(db.Float)
    dni10 = db.Column(db.Float)
    dni90 = db.Column(db.Float)
    dhi = db.Column(db.Float)
    air_temp = db.Column(db.Float)
    zenith = db.Column(db.Float)
    azimuth = db.Column(db.Float)
    cloud_opacity = db.Column(db.Float)