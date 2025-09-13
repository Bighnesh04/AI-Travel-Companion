import folium
import requests
from typing import List, Tuple
import re

class MapGenerator:
    def __init__(self):
        self.default_zoom = 12
    
    def get_coordinates(self, location_name: str) -> Tuple[float, float]:
        """Get coordinates for a location using Nominatim (OpenStreetMap) API"""
        try:
            # Use Nominatim API (free, no API key required)
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': location_name,
                'format': 'json',
                'limit': 1
            }
            
            headers = {
                'User-Agent': 'AI-Travel-Companion/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                # Default coordinates for major cities if API fails
                default_coords = {
                    'paris': (48.8566, 2.3522),
                    'london': (51.5074, -0.1278),
                    'new york': (40.7128, -74.0060),
                    'tokyo': (35.6762, 139.6503),
                    'rome': (41.9028, 12.4964),
                    'barcelona': (41.3851, 2.1734),
                }
                
                for city, coords in default_coords.items():
                    if city in location_name.lower():
                        return coords
                
                return 48.8566, 2.3522  # Default to Paris
                
        except Exception as e:
            print(f"Error getting coordinates for {location_name}: {str(e)}")
            return 48.8566, 2.3522  # Default to Paris
    
    def create_itinerary_map(self, destination: str, attractions: List[str] = None) -> folium.Map:
        """Create an interactive map with itinerary locations"""
        
        # Get destination coordinates
        dest_lat, dest_lon = self.get_coordinates(destination)
        
        # Create base map
        m = folium.Map(
            location=[dest_lat, dest_lon],
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )
        
        # Add destination marker
        folium.Marker(
            [dest_lat, dest_lon],
            popup=folium.Popup(f"<b>{destination}</b><br>Main Destination", max_width=200),
            tooltip=destination,
            icon=folium.Icon(color='red', icon='star', prefix='fa')
        ).add_to(m)
        
        # Default attractions for demo purposes
        if not attractions:
            attractions = [
                "Eiffel Tower, Paris",
                "Louvre Museum, Paris",
                "Notre-Dame Cathedral, Paris",
                "Arc de Triomphe, Paris",
                "Sacré-Cœur, Paris"
            ]
        
        # Add attraction markers
        colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue']
        
        for i, attraction in enumerate(attractions):
            try:
                lat, lon = self.get_coordinates(attraction)
                color = colors[i % len(colors)]
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(f"<b>{attraction}</b><br>Tourist Attraction", max_width=200),
                    tooltip=attraction,
                    icon=folium.Icon(color=color, icon='map-marker', prefix='fa')
                ).add_to(m)
                
            except Exception as e:
                print(f"Error adding marker for {attraction}: {str(e)}")
                continue
        
        # Add a circle around the main destination
        folium.Circle(
            location=[dest_lat, dest_lon],
            radius=5000,  # 5km radius
            popup="Main Area",
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.1
        ).add_to(m)
        
        return m
    
    def create_restaurant_map(self, destination: str, restaurants: List[str] = None) -> folium.Map:
        """Create a map focusing on restaurant locations"""
        
        dest_lat, dest_lon = self.get_coordinates(destination)
        
        m = folium.Map(
            location=[dest_lat, dest_lon],
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )
        
        # Add destination marker
        folium.Marker(
            [dest_lat, dest_lon],
            popup=f"<b>{destination}</b>",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)
        
        # Default restaurants for demo
        if not restaurants:
            restaurants = [
                "Le Comptoir du Relais, Paris",
                "L'As du Fallafel, Paris",
                "Breizh Café, Paris",
                "Pierre Hermé, Paris"
            ]
        
        # Add restaurant markers
        for restaurant in restaurants:
            try:
                lat, lon = self.get_coordinates(restaurant)
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(f"<b>{restaurant}</b><br>Restaurant", max_width=200),
                    tooltip=restaurant,
                    icon=folium.Icon(color='orange', icon='cutlery', prefix='fa')
                ).add_to(m)
                
            except Exception as e:
                print(f"Error adding restaurant marker: {str(e)}")
                continue
        
        return m
    
    def extract_locations_from_itinerary(self, itinerary_text: str) -> List[str]:
        """Extract location names from itinerary text"""
        
        # Simple regex patterns to find locations
        # This is a basic implementation - could be enhanced with NLP
        patterns = [
            r'visit\s+([A-Z][a-zA-Z\s]+)',
            r'explore\s+([A-Z][a-zA-Z\s]+)',
            r'see\s+([A-Z][a-zA-Z\s]+)',
            r'go to\s+([A-Z][a-zA-Z\s]+)',
        ]
        
        locations = []
        for pattern in patterns:
            matches = re.findall(pattern, itinerary_text)
            locations.extend(matches)
        
        # Clean up locations (remove common words)
        clean_locations = []
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        
        for location in locations:
            words = location.strip().split()
            if len(words) > 0 and words[0].lower() not in common_words:
                clean_locations.append(location.strip())
        
        return list(set(clean_locations))  # Remove duplicates