from flask import Flask
from models import db, Location
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///solar_forecast.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        if Location.query.count() == 0:
            solar_one = Location(
                name="Solar_One_Plant",
                latitude=7.976510,
                longitude=81.236602,
                api_key="kAVziMj4__x-RQ9Ab67-TBwv2ry_Z9uY",
                grid_substation="Polonnaruwa GSS",
                feeder_number="Feeder_01"
            )
            db.session.add(solar_one)
            db.session.commit()
        print("Database initialized.")

if __name__ == "__main__":
    init_db()