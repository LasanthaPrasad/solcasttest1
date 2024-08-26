from flask import Flask, render_template, request, redirect, url_for
import requests
import matplotlib.pyplot as plt
import io
import base64
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///solar_forecast.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SOLCAST_API_KEY = os.environ.get('SOLCAST_API_KEY')

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

@app.route('/')
def index():
    locations = Location.query.all()
    return render_template('index.html', locations=locations)

@app.route('/location/<int:id>')
def location_forecast(id):
    location = Location.query.get_or_404(id)
    api_key = location.api_key or SOLCAST_API_KEY
    url = f'https://api.solcast.com.au/world_radiation/forecasts?latitude={location.latitude}&longitude={location.longitude}&api_key={api_key}&format=json'
    response = requests.get(url)
    data = response.json()

    # Clear old forecasts
    Forecast.query.filter_by(location_id=location.id).delete()

    # Store new forecasts
    for entry in data['forecasts']:
        forecast = Forecast(
            location_id=location.id,
            timestamp=datetime.fromisoformat(entry['period_end']),
            ghi=entry['ghi'],
            ghi90=entry['ghi90'],
            ghi10=entry['ghi10'],
            ebh=entry['ebh'],
            dni=entry['dni'],
            dni10=entry['dni10'],
            dni90=entry['dni90'],
            dhi=entry['dhi'],
            air_temp=entry['air_temp'],
            zenith=entry['zenith'],
            azimuth=entry['azimuth'],
            cloud_opacity=entry['cloud_opacity']
        )
        db.session.add(forecast)
    db.session.commit()

    # Create plot
    plt.figure(figsize=(12, 6))
    forecasts = Forecast.query.filter_by(location_id=location.id).order_by(Forecast.timestamp).all()
    timestamps = [f.timestamp for f in forecasts]
    for attr in ['ghi', 'ghi90', 'ghi10', 'ebh', 'dni', 'dni10', 'dni90', 'dhi', 'air_temp', 'zenith', 'azimuth', 'cloud_opacity']:
        values = [getattr(f, attr) for f in forecasts]
        plt.plot(timestamps, values, label=attr)

    plt.title(f'Solar Forecast for {location.name}')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return render_template('forecast.html', location=location, plot_url=plot_url)

@app.route('/location/new', methods=['GET', 'POST'])
def new_location():
    if request.method == 'POST':
        location = Location(
            name=request.form['name'],
            api_key=request.form['api_key'] or None,
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude']),
            grid_substation=request.form['grid_substation'],
            feeder_number=request.form['feeder_number']
        )
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('location_form.html')

@app.route('/location/<int:id>/edit', methods=['GET', 'POST'])
def edit_location(id):
    location = Location.query.get_or_404(id)
    if request.method == 'POST':
        location.name = request.form['name']
        location.api_key = request.form['api_key'] or None
        location.latitude = float(request.form['latitude'])
        location.longitude = float(request.form['longitude'])
        location.grid_substation = request.form['grid_substation']
        location.feeder_number = request.form['feeder_number']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('location_form.html', location=location)

@app.route('/location/<int:id>/delete', methods=['POST'])
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('index'))

@app.cli.command("init-db")
def init_db():
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)