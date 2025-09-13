import google.generativeai as genai
import os
from datetime import datetime

class ItineraryGenerator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Updated model name - gemini-pro is deprecated
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_itinerary(self, destination, start_date, end_date, budget, interests, traveler_type, weather_info=None):
        """Generate a detailed travel itinerary using Gemini AI"""
        
        # Calculate trip duration
        duration = (end_date - start_date).days + 1
        
        # Create detailed prompt
        prompt = f"""
        Create a detailed {duration}-day travel itinerary for {destination}.
        
        Travel Details:
        - Destination: {destination}
        - Dates: {start_date} to {end_date}
        - Duration: {duration} days
        - Budget: {budget}
        - Traveler Type: {traveler_type}
        - Interests: {', '.join(interests)}
        
        {f"Weather Information: {weather_info}" if weather_info else ""}
        
        Please provide:
        1. Day-by-day detailed itinerary with specific activities and timings
        2. Recommended restaurants and dining options
        3. Transportation suggestions between locations
        4. Estimated costs for each activity (aligned with budget)
        5. Insider tips and local recommendations
        6. Best times to visit attractions to avoid crowds
        
        Format the response clearly with day headers and detailed activities.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate itinerary: {str(e)}")
    
    def get_restaurant_recommendations(self, destination, cuisine_preferences=None):
        """Get restaurant recommendations for a destination"""
        
        prompt = f"""
        Recommend the top 10 restaurants in {destination}.
        
        Include:
        - Restaurant name and type of cuisine
        - Brief description
        - Price range
        - Must-try dishes
        - Location/area
        
        {f"Preferred cuisines: {cuisine_preferences}" if cuisine_preferences else "Include variety of local and international cuisines"}
        
        Format as a clear list with details for each restaurant.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to get restaurant recommendations: {str(e)}")
    
    def get_attraction_recommendations(self, destination, interests):
        """Get attraction recommendations based on interests"""
        
        prompt = f"""
        Recommend top attractions in {destination} based on these interests: {', '.join(interests)}.
        
        For each attraction, provide:
        - Name and brief description
        - Why it matches the specified interests
        - Best time to visit
        - Approximate duration needed
        - Entrance fees (if any)
        - Insider tips
        
        Include both popular attractions and hidden gems.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to get attraction recommendations: {str(e)}")
    
    def get_travel_tips(self, destination):
        """Get comprehensive travel tips for a destination"""
        
        prompt = f"""
        Provide comprehensive travel tips for {destination} including:
        
        1. **Cultural Tips**:
           - Local customs and etiquette
           - Cultural do's and don'ts
           - Tipping practices
        
        2. **Safety Information**:
           - General safety tips
           - Areas to avoid
           - Emergency contacts
        
        3. **Practical Information**:
           - Best time to visit
           - Currency and payment methods
           - Language tips and useful phrases
           - Transportation options
        
        4. **Local Insights**:
           - Hidden gems only locals know
           - Best neighborhoods to explore
           - Seasonal events and festivals
        
        5. **Money-Saving Tips**:
           - Free activities and attractions
           - Best value dining options
           - Transportation hacks
        
        Format the response with clear sections and actionable advice.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to get travel tips: {str(e)}")