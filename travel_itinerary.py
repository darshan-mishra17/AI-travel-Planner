import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
def configure_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("API key not found in .env file. Please create a .env file with GOOGLE_API_KEY=your_api_key")
        st.stop()
    genai.configure(api_key=api_key)

def main():
    # Custom CSS for styling
    st.markdown("""
    <style>
    .itinerary-day {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .itinerary-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    .activity {
        margin-left: 20px;
        padding-left: 10px;
        border-left: 3px solid #3498db;
    }
    .restaurant {
        background-color: #e8f4fc;
        padding: 8px;
        border-radius: 5px;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌍 Mera Bharat Yatra")
    st.subheader("Plan your perfect trip with AI!")
    
    # Configure Gemini
    configure_gemini()
    
    # Trip details form
    with st.form("travel_preferences"):
        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input("Destination", placeholder="Where do you want to go?")
            num_people = st.number_input("Number of travelers", min_value=1, max_value=20, value=2)
            num_days = st.number_input("Number of days", min_value=1, max_value=30, value=5)
        
        with col2:
            start_date = st.date_input("Start date", min_value=datetime.now().date())
            end_date = st.date_input("End date", 
                                    min_value=start_date, 
                                    value=start_date + timedelta(days=num_days-1),
                                    disabled=True)
        
        travel_types = ["Leisure", "Business", "Backpacking", "Family", "Honeymoon", "Solo"]
        travel_type = st.selectbox("Type of travel", travel_types)
        
        st.subheader("Your Interests (Rate 1-10)")
        col1, col2 = st.columns(2)
        with col1:
            art = st.slider("Art & Culture", 0, 10, 5, key="art")
            heritage = st.slider("Heritage", 0, 10, 5, key="heritage")
            spirituality = st.slider("Spirituality", 0, 10, 3, key="spirituality")
        with col2:
            nightlife = st.slider("Nightlife", 0, 10, 4, key="nightlife")
            adventure = st.slider("Adventure", 0, 10, 6, key="adventure")
            nature = st.slider("Nature", 0, 10, 7, key="nature")
        
        budget = st.selectbox("Budget Level", ["Budget", "Mid-range", "Luxury"], index=1)
        
        # Submit button - THIS WAS MISSING
        submitted = st.form_submit_button("Generate Itinerary", type="primary")
    
    if submitted:
        if not destination:
            st.error("Please enter a destination")
            return
        
        with st.spinner("✨ Creating your personalized itinerary..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                
                prompt = f"""
                Create a detailed {num_days}-day travel itinerary for {destination} for {num_people} {travel_type.lower()} travelers.
                
                Travel dates: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}
                Budget level: {budget}
                
                Interests (scale 1-10):
                - Art & Culture: {art}/10
                - Heritage: {heritage}/10
                - Spirituality: {spirituality}/10
                - Nightlife: {nightlife}/10
                - Adventure: {adventure}/10
                - Nature: {nature}/10
                
                The itinerary should:
                - Include daily schedules with time slots
                - Recommend activities matching the interests
                - Suggest restaurants matching the budget
                - Include transportation tips
                - Add special notes based on travel type
                
                Format the response with these tags:
                <day>Day 1: Title</day>
                <time>9:00 AM</time> <activity>Activity description</activity>
                <restaurant>Restaurant name</restaurant>
                <note>Special tip</note>
                """
                
                response = model.generate_content(prompt)
                
                # Process and display the formatted response
                st.success("## Here's Your Personalized Itinerary")
                st.markdown(f"### ✈️ {destination} | 📅 {start_date.strftime('%b %d')} - {end_date.strftime('%b %d')} | 👪 {num_people} travelers")
                
                # Convert response to formatted Markdown
                formatted_response = response.text
                formatted_response = formatted_response.replace("<day>", "### 🗓️ ").replace("</day>", "")
                formatted_response = formatted_response.replace("<time>", "**⏰ ").replace("</time>", "**")
                formatted_response = formatted_response.replace("<activity>", "\n• ").replace("</activity>", "")
                formatted_response = formatted_response.replace("<restaurant>", "🍴 ").replace("</restaurant>", "")
                formatted_response = formatted_response.replace("<note>", "\n> 💡 **Tip:** ").replace("</note>", "")
                
                st.markdown(formatted_response, unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Itinerary",
                    data=response.text,
                    file_name=f"{destination}_itinerary_{start_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"Error generating itinerary: {str(e)}")

if __name__ == "__main__":
    main()