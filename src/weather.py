import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather_forecast(self, destination: str, days: int = 5) -> Optional[Dict]:
        """Get weather forecast for a destination"""
        
        if not self.api_key:
            return None  # Weather is optional
        
        try:
            # Get coordinates first
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                'q': destination,
                'limit': 1,
                'appid': self.api_key
            }
            
            geo_response = requests.get(geocoding_url, params=geo_params)
            geo_data = geo_response.json()
            
            if not geo_data:
                return None
            
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            
            # Get forecast
            forecast_url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (every 3 hours)
            }
            
            response = requests.get(forecast_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                return self._process_forecast_data(data)
            else:
                return None
                
        except Exception as e:
            print(f"Weather service error: {str(e)}")
            return None
    
    def _process_forecast_data(self, data: Dict) -> Dict:
        """Process raw weather data into useful format"""
        
        forecasts = data.get('list', [])
        daily_forecasts = {}
        
        for forecast in forecasts:
            date = datetime.fromtimestamp(forecast['dt']).date()
            date_str = date.strftime('%Y-%m-%d')
            
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    'date': date_str,
                    'temps': [],
                    'conditions': [],
                    'humidity': [],
                    'wind_speed': []
                }
            
            daily_forecasts[date_str]['temps'].append(forecast['main']['temp'])
            daily_forecasts[date_str]['conditions'].append(forecast['weather'][0]['description'])
            daily_forecasts[date_str]['humidity'].append(forecast['main']['humidity'])
            daily_forecasts[date_str]['wind_speed'].append(forecast['wind']['speed'])
        
        # Calculate daily averages
        processed_forecasts = {}
        for date_str, day_data in daily_forecasts.items():
            processed_forecasts[date_str] = {
                'date': date_str,
                'avg_temp': round(sum(day_data['temps']) / len(day_data['temps']), 1),
                'max_temp': round(max(day_data['temps']), 1),
                'min_temp': round(min(day_data['temps']), 1),
                'condition': max(set(day_data['conditions']), key=day_data['conditions'].count),
                'humidity': round(sum(day_data['humidity']) / len(day_data['humidity'])),
                'wind_speed': round(sum(day_data['wind_speed']) / len(day_data['wind_speed']), 1)
            }
        
        return {
            'location': data['city']['name'],
            'forecasts': processed_forecasts
        }
    
    def get_weather_summary(self, destination: str) -> str:
        """Get a human-readable weather summary"""
        
        forecast_data = self.get_weather_forecast(destination)
        
        if not forecast_data:
            return "Weather information not available"
        
        forecasts = forecast_data['forecasts']
        if not forecasts:
            return "Weather forecast not available"
        
        # Get first few days
        summary_parts = []
        for i, (date_str, forecast) in enumerate(list(forecasts.items())[:3]):
            day_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
            summary_parts.append(
                f"{day_name}: {forecast['condition']}, "
                f"High {forecast['max_temp']}°C, Low {forecast['min_temp']}°C"
            )
        
        return "Weather Forecast:\n" + "\n".join(summary_parts)