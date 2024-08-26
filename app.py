    
from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

SOLCAST_API_KEY = os.environ.get('SOLCAST_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        
        # Make API request to Solcast
        url = f'https://api.solcast.com.au/world_radiation/forecasts?latitude={latitude}&longitude={longitude}&api_key={SOLCAST_API_KEY}&format=json'
        response = requests.get(url)
        data = response.json()
        
        # Extract relevant data for plotting
        timestamps = [entry['period_end'] for entry in data['forecasts']]
        ghi = [entry['ghi'] for entry in data['forecasts']]
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, ghi)
        plt.title(f'Solar Irradiation Forecast for Lat: {latitude}, Long: {longitude}')
        plt.xlabel('Time')
        plt.ylabel('Global Horizontal Irradiance (W/m²)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Encode plot to base64 string
        plot_url = base64.b64encode(buf.getvalue()).decode('utf8')
        
        return render_template('result.html', plot_url=plot_url)
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)