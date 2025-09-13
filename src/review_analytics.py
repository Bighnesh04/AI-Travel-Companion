import google.generativeai as genai
import json
import re
from collections import Counter
from typing import Dict, List

class ReviewAnalyzer:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Updated model name - gemini-pro is deprecated
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_reviews(self, reviews_text: str) -> Dict:
        """Analyze multiple reviews for sentiment and insights"""
        
        # Split reviews (assuming they're separated by double line breaks or numbers)
        reviews = self._split_reviews(reviews_text)
        
        if not reviews:
            return {"error": "No valid reviews found"}
        
        # Analyze sentiment for each review
        sentiments = []
        
        for review in reviews:
            if len(review.strip()) > 10:  # Only analyze substantial reviews
                sentiment = self._analyze_single_review_sentiment(review)
                sentiments.append(sentiment)
        
        # Get overall insights
        overall_insights = self._get_overall_insights(reviews_text)
        
        # Calculate sentiment distribution
        sentiment_counts = Counter(sentiments)
        total_reviews = len(sentiments)
        
        sentiment_distribution = {
            'Positive': sentiment_counts.get('positive', 0),
            'Neutral': sentiment_counts.get('neutral', 0),
            'Negative': sentiment_counts.get('negative', 0)
        }
        
        # Generate summary insights
        summary_insights = self._generate_summary_insights(sentiment_distribution, total_reviews)
        
        return {
            'total_reviews': total_reviews,
            'sentiment_distribution': sentiment_distribution,
            'insights': overall_insights + summary_insights,
            'sentiment_percentages': {
                k: round((v/total_reviews)*100, 1) if total_reviews > 0 else 0 
                for k, v in sentiment_distribution.items()
            }
        }
    
    def _split_reviews(self, text: str) -> List[str]:
        """Split text into individual reviews"""
        
        # Try different splitting methods
        
        # Method 1: Split by double line breaks
        reviews = text.split('\n\n')
        if len(reviews) > 1:
            return [r.strip() for r in reviews if r.strip()]
        
        # Method 2: Split by numbered reviews (1., 2., etc.)
        numbered_pattern = r'\d+\.\s*'
        reviews = re.split(numbered_pattern, text)
        if len(reviews) > 1:
            return [r.strip() for r in reviews if r.strip()]
        
        # Method 3: Split by "Review:" pattern
        review_pattern = r'Review\s*:?\s*'
        reviews = re.split(review_pattern, text, flags=re.IGNORECASE)
        if len(reviews) > 1:
            return [r.strip() for r in reviews if r.strip()]
        
        # Method 4: If no clear separation, treat as single review
        return [text.strip()] if text.strip() else []
    
    def _analyze_single_review_sentiment(self, review: str) -> str:
        """Analyze sentiment of a single review"""
        
        prompt = f"""
        Analyze the sentiment of this review and respond with ONLY one word: positive, negative, or neutral.
        
        Review: "{review}"
        
        Response (one word only):
        """
        
        try:
            response = self.model.generate_content(prompt)
            sentiment = response.text.strip().lower()
            
            # Ensure we get a valid response
            if sentiment in ['positive', 'negative', 'neutral']:
                return sentiment
            elif 'positive' in sentiment:
                return 'positive'
            elif 'negative' in sentiment:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return 'neutral'
    
    def _get_overall_insights(self, reviews_text: str) -> List[str]:
        """Get overall insights from all reviews"""
        
        prompt = f"""
        Analyze these travel reviews and provide 5-7 key insights about the destination/experience.
        Focus on:
        - Common positive aspects mentioned
        - Common complaints or issues
        - Recommendations that appear frequently
        - Notable patterns in visitor experiences
        
        Reviews:
        {reviews_text}
        
        Provide insights as a list of clear, actionable points.
        """
        
        try:
            response = self.model.generate_content(prompt)
            insights_text = response.text
            
            # Parse insights into list
            insights = []
            lines = insights_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    insight = line.lstrip('•-* ').strip()
                    if insight:
                        insights.append(insight)
                elif line and len(line.split()) > 3:  # Substantial line
                    insights.append(line)
            
            return insights[:7]  # Limit to 7 insights
            
        except Exception as e:
            print(f"Error getting insights: {str(e)}")
            return ["Unable to generate insights from reviews"]
    
    def _generate_summary_insights(self, sentiment_dist: Dict, total_reviews: int) -> List[str]:
        """Generate summary insights based on sentiment distribution"""
        
        if total_reviews == 0:
            return []
        
        insights = []
        
        positive_pct = (sentiment_dist['Positive'] / total_reviews) * 100
        negative_pct = (sentiment_dist['Negative'] / total_reviews) * 100
        
        if positive_pct > 70:
            insights.append("Overwhelmingly positive reviews - visitors love this destination!")
        elif positive_pct > 50:
            insights.append("Generally positive sentiment with most visitors having good experiences")
        elif negative_pct > 50:
            insights.append("Concerning number of negative reviews - consider investigating common issues")
        else:
            insights.append("Mixed reviews with varied visitor experiences")
        
        if sentiment_dist['Positive'] > sentiment_dist['Negative'] * 2:
            insights.append("Strong positive sentiment indicates high visitor satisfaction")
        
        return insights