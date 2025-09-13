import streamlit as st
import os
from datetime import datetime, date
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from src.itinerary import ItineraryGenerator
from src.maps import MapGenerator
from src.review_analytics import ReviewAnalyzer
from src.weather import WeatherService
from src.export_utils import ExportManager

# Page configuration
st.set_page_config(
    page_title="AI Travel Companion",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'map_data' not in st.session_state:
    st.session_state.map_data = None
if 'reviews_analyzed' not in st.session_state:
    st.session_state.reviews_analyzed = None

def get_api_key():
    """Try to load API key from environment with fallback"""
    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("GOOGLE_GEMINI_API_KEY")
    )
    return api_key

def main():
    # Header section
    st.title("🌍 AI Travel Companion")
    st.markdown("**Your intelligent travel planning assistant powered by Google Gemini AI**")
    
    # Add some spacing
    st.divider()
    
    # Sidebar for API key configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Try to get API key from environment first
        env_api_key = get_api_key()
        
        # API Key input with better handling
        if env_api_key:
            st.success("✅ API Key loaded from environment!")
            api_key = env_api_key
            # Still show input but make it optional
            manual_api_key = st.text_input(
                "Override API Key (optional)", 
                value="",
                type="password",
                help="Leave empty to use the API key from your .env file"
            )
            if manual_api_key:
                api_key = manual_api_key
                st.info("Using manually entered API key")
        else:
            api_key = st.text_input(
                "Gemini API Key", 
                value="",
                type="password",
                help="Enter your Google Gemini API key. Get one from Google AI Studio."
            )
            
            if not api_key:
                st.error("⚠️ No API key found!")
                st.markdown("""
                **To fix this:**
                1. Create a `.env` file in your project root
                2. Add: `GEMINI_API_KEY=your_api_key_here`
                3. Restart the app
                
                OR enter your API key above.
                """)
                st.info("Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        
        # Set environment variable for the session
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        
        st.divider()
        st.subheader("🔗 Quick Links")
        st.markdown("- [Google AI Studio](https://makersuite.google.com/app/apikey)")
        st.markdown("- [Project Documentation](https://github.com)")
        st.markdown("- [Report Issues](https://github.com)")
        
        # Add feature highlights in sidebar
        st.divider()
        st.subheader("✨ Features")
        st.markdown("🗓️ **Personalized Itineraries**")
        st.markdown("🗺️ **Interactive Maps**")
        st.markdown("📊 **Review Analytics**")
        st.markdown("💡 **Travel Tips**")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗓️ Itinerary Planner", 
        "🗺️ Map View", 
        "📊 Review Analytics", 
        "💡 Travel Tips"
    ])
    
    with tab1:
        itinerary_planner_tab(api_key)
    
    with tab2:
        map_view_tab()
    
    with tab3:
        review_analytics_tab(api_key)
    
    with tab4:
        travel_tips_tab(api_key)

def itinerary_planner_tab(api_key):
    st.header("🗓️ Plan Your Perfect Trip")
    
    if not api_key:
        st.error("Please configure your Gemini API key in the sidebar to use this feature.")
        return
    
    # Feature description
    st.info("Create personalized travel itineraries based on your preferences, budget, and interests!")
    
    # Input form
    with st.form("itinerary_form"):
        st.subheader("📝 Trip Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input(
                "🎯 Destination", 
                placeholder="e.g., Paris, France",
                help="Enter the city or country you want to visit"
            )
            start_date = st.date_input(
                "📅 Start Date", 
                value=date.today(),
                help="When does your trip begin?"
            )
            budget = st.selectbox(
                "💰 Budget Range", 
                [
                    "Budget ($0-50/day)", 
                    "Mid-range ($50-150/day)", 
                    "Luxury ($150+/day)"
                ],
                help="Select your daily budget range"
            )
        
        with col2:
            end_date = st.date_input(
                "📅 End Date", 
                value=date.today(),
                help="When does your trip end?"
            )
            interests = st.multiselect(
                "🎨 Interests", 
                [
                    "History & Culture", "Food & Dining", "Outdoor Activities", 
                    "Museums & Art", "Shopping", "Nightlife", "Architecture", 
                    "Nature & Parks", "Adventure Sports", "Local Experiences"
                ],
                help="Select what interests you most"
            )
            traveler_type = st.selectbox(
                "👥 Traveler Type", 
                [
                    "Solo Traveler", "Couple", "Family with Kids", 
                    "Friends Group", "Business"
                ],
                help="Who are you traveling with?"
            )
        
        # Form validation
        duration = (end_date - start_date).days + 1
        if duration <= 0:
            st.error("End date must be after start date!")
        elif duration > 30:
            st.warning("Long trips (>30 days) may take more time to generate.")
        else:
            st.success(f"Trip duration: {duration} days")
        
        submit_button = st.form_submit_button(
            "🚀 Generate Itinerary", 
            use_container_width=True,
            type="primary"
        )
    
    # Generate itinerary
    if submit_button and destination and interests and duration > 0:
        with st.spinner("🤖 AI is crafting your perfect itinerary... This may take a moment."):
            try:
                generator = ItineraryGenerator(api_key)
                weather_service = WeatherService()
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Get weather data (optional)
                status_text.text("Getting weather information...")
                progress_bar.progress(25)
                weather_info = weather_service.get_weather_forecast(destination)
                
                # Generate itinerary
                status_text.text("Generating personalized itinerary...")
                progress_bar.progress(75)
                itinerary = generator.generate_itinerary(
                    destination=destination,
                    start_date=start_date,
                    end_date=end_date,
                    budget=budget,
                    interests=interests,
                    traveler_type=traveler_type,
                    weather_info=weather_info
                )
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                
                st.session_state.itinerary = itinerary
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display itinerary
                display_itinerary(itinerary)
                
                # Export options
                export_section(itinerary, destination)
                
            except Exception as e:
                st.error(f"❌ Error generating itinerary: {str(e)}")
                st.info("Please check your API key and try again.")
    
    # Display cached itinerary if available
    elif st.session_state.itinerary:
        st.info("Showing previously generated itinerary:")
        display_itinerary(st.session_state.itinerary)
        export_section(st.session_state.itinerary, destination or "Travel")

def display_itinerary(itinerary):
    st.success("✅ Your personalized itinerary is ready!")
    
    # Parse and display the itinerary
    days = itinerary.split("Day ")
    
    if len(days) <= 1:
        # If no clear day separation, display as single text
        st.markdown(itinerary)
    else:
        # Display each day in expandable sections
        for i, day_content in enumerate(days[1:], 1):
            with st.expander(f"📅 Day {i}", expanded=i == 1):
                st.markdown(f"**Day {i}**")
                st.markdown(day_content)
    
    # Add helpful note
    st.info("💡 **Tip:** This itinerary is AI-generated. Always verify opening hours, prices, and availability before your trip!")

def export_section(itinerary, destination):
    st.divider()
    st.subheader("📥 Export Your Itinerary")
    st.markdown("Save your itinerary for offline access!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate PDF", use_container_width=True):
            try:
                with st.spinner("Creating PDF..."):
                    export_manager = ExportManager()
                    pdf_buffer = export_manager.export_to_pdf(itinerary, destination)
                    st.success("PDF generated successfully!")
                    st.download_button(
                        label="💾 Download PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"{destination.replace(' ', '_')}_itinerary.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        if st.button("📝 Generate Markdown", use_container_width=True):
            try:
                with st.spinner("Creating Markdown..."):
                    export_manager = ExportManager()
                    markdown_content = export_manager.export_to_markdown(itinerary, destination)
                    st.success("Markdown generated successfully!")
                    st.download_button(
                        label="💾 Download Markdown",
                        data=markdown_content,
                        file_name=f"{destination.replace(' ', '_')}_itinerary.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error generating Markdown: {str(e)}")
    
    with col3:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.code(itinerary, language=None)
            st.info("Copy the text above to your clipboard!")

def map_view_tab():
    st.header("🗺️ Interactive Travel Map")
    
    if not st.session_state.itinerary:
        st.info("💡 Generate an itinerary first to see locations on the map!")
        st.markdown("**Map features:**")
        st.markdown("- 📍 Interactive location markers")
        st.markdown("- 🗺️ Zoom and pan functionality") 
        st.markdown("- 📱 Mobile-friendly interface")
        return
    
    st.success("Displaying map based on your itinerary!")
    
    # Map controls
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🎛️ Map Controls")
        map_style = st.selectbox(
            "Map Style",
            ["OpenStreetMap", "Satellite", "Terrain"]
        )
        show_attractions = st.checkbox("Show Attractions", value=True)
        show_restaurants = st.checkbox("Show Restaurants", value=True)
    
    with col1:
        # Map generation
        try:
            map_generator = MapGenerator()
            
            # Extract destination from session or use default
            destination = "Paris, France"  # You could extract this from the itinerary
            
            travel_map = map_generator.create_itinerary_map(destination)
            
            # Display map
            st_folium(travel_map, width=700, height=500, returned_objects=["last_object_clicked"])
            
        except Exception as e:
            st.error(f"❌ Error loading map: {str(e)}")
            st.info("Please check your internet connection and try again.")

def review_analytics_tab(api_key):
    st.header("📊 Review Analytics Dashboard")
    
    if not api_key:
        st.error("Please configure your Gemini API key in the sidebar to use this feature.")
        return
    
    st.info("Analyze traveler reviews to get insights about destinations using AI-powered sentiment analysis!")
    
    # Review input section
    st.subheader("📝 Input Reviews")
    review_input_method = st.radio(
        "Choose how to input reviews:",
        ["Paste Reviews", "Upload File"],
        horizontal=True
    )
    
    reviews_text = ""
    
    if review_input_method == "Paste Reviews":
        reviews_text = st.text_area(
            "📝 Paste reviews here:",
            height=200,
            placeholder="Paste multiple reviews separated by line breaks...\n\nExample:\nGreat hotel with amazing service!\n\nFood was okay but location was perfect.\n\nWould not recommend, very noisy."
        )
    else:
        uploaded_file = st.file_uploader(
            "Choose a text file", 
            type=['txt'],
            help="Upload a .txt file containing reviews"
        )
        if uploaded_file:
            reviews_text = str(uploaded_file.read(), "utf-8")
            st.success(f"File uploaded! Contains {len(reviews_text)} characters.")
    
    # Analysis button
    if st.button("🔍 Analyze Reviews", use_container_width=True, type="primary") and reviews_text:
        with st.spinner("🤖 Analyzing sentiment and extracting insights..."):
            try:
                analyzer = ReviewAnalyzer(api_key)
                results = analyzer.analyze_reviews(reviews_text)
                
                st.session_state.reviews_analyzed = results
                
                # Display results
                display_review_analytics(results)
                
            except Exception as e:
                st.error(f"❌ Error analyzing reviews: {str(e)}")
                st.info("Please check your API key and try again.")
    
    # Display cached results
    elif st.session_state.reviews_analyzed:
        st.info("Showing previously analyzed results:")
        display_review_analytics(st.session_state.reviews_analyzed)

def display_review_analytics(results):
    """Display review analytics using pure Streamlit components"""
    st.success("✅ Analysis Complete!")
    
    # Check if there's an error in results
    if 'error' in results:
        st.error(f"Analysis error: {results['error']}")
        return
    
    # Summary metrics at the top
    st.subheader("📈 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", results.get('total_reviews', 0))
    
    with col2:
        positive_pct = results.get('sentiment_percentages', {}).get('Positive', 0)
        st.metric("Positive Reviews", f"{positive_pct}%")
    
    with col3:
        neutral_pct = results.get('sentiment_percentages', {}).get('Neutral', 0)
        st.metric("Neutral Reviews", f"{neutral_pct}%")
    
    with col4:
        negative_pct = results.get('sentiment_percentages', {}).get('Negative', 0)
        st.metric("Negative Reviews", f"{negative_pct}%")
    
    st.divider()
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("😊 Sentiment Distribution")
        sentiment_data = results.get('sentiment_distribution', {})
        
        if sentiment_data:
            # Create simple bar chart using Streamlit
            st.bar_chart(sentiment_data)
            
            # Show raw numbers
            st.markdown("**Raw counts:**")
            for sentiment, count in sentiment_data.items():
                st.write(f"• {sentiment}: {count} reviews")
        else:
            st.info("No sentiment data available")
    
    with col2:
        st.subheader("💡 Key Insights")
        insights = results.get('insights', [])
        
        if insights:
            for i, insight in enumerate(insights, 1):
                st.write(f"{i}. {insight}")
        else:
            st.info("No insights available")
    
    # Additional analysis
    st.divider()
    st.subheader("🎯 Recommendations")
    
    # Generate recommendations based on sentiment
    positive_pct = results.get('sentiment_percentages', {}).get('Positive', 0)
    negative_pct = results.get('sentiment_percentages', {}).get('Negative', 0)
    
    if positive_pct > 70:
        st.success("🌟 **Highly Recommended!** This destination receives overwhelmingly positive reviews.")
    elif positive_pct > 50:
        st.info("👍 **Generally Good** - Most visitors have positive experiences.")
    elif negative_pct > 50:
        st.warning("⚠️ **Mixed Reviews** - Consider reading detailed feedback before visiting.")
    else:
        st.info("📊 **Balanced Feedback** - Reviews show varied experiences.")

def travel_tips_tab(api_key):
    st.header("💡 Smart Travel Tips")
    
    if not api_key:
        st.error("Please configure your Gemini API key in the sidebar to use this feature.")
        return
    
    st.info("Get personalized travel tips and local insights powered by AI!")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        destination = st.text_input(
            "🌍 Enter destination for personalized tips:",
            placeholder="e.g., Tokyo, Japan"
        )
    
    with col2:
        st.markdown("**Tip categories:**")
        st.markdown("• Cultural insights")
        st.markdown("• Safety information")
        st.markdown("• Money-saving tips")
        st.markdown("• Hidden gems")
    
    if destination and st.button("🧠 Get AI Travel Tips", use_container_width=True, type="primary"):
        with st.spinner("🤖 Gathering local insights and tips..."):
            try:
                generator = ItineraryGenerator(api_key)
                tips = generator.get_travel_tips(destination)
                
                st.success(f"✅ Tips generated for {destination}!")
                st.divider()
                
                # Display tips in an organized way
                st.markdown("### 🎯 Personalized Tips")
                st.markdown(tips)
                
                # Add export option for tips
                st.divider()
                if st.button("📋 Copy Tips", use_container_width=True):
                    st.code(tips, language=None)
                    st.info("Copy the tips above to save them!")
                
            except Exception as e:
                st.error(f"❌ Error getting travel tips: {str(e)}")
                st.info("Please check your API key and try again.")

if __name__ == "__main__":
    main()