from pytrends.request import TrendReq
import streamlit as st
import re
import time

# Dictionary with countries and states using Google Trends-compatible geo codes
country_states = {
    "United States": {"code": "US", "states": {"California": "US-CA", "Texas": "US-TX", "New York": "US-NY"}},
    "India": {"code": "IN", "states": {"Maharashtra": "IN-MH", "Karnataka": "IN-KA", "Delhi": "IN-DL"}},
}

# Function to sanitize the keyword
def sanitize_keyword(keyword):
    return re.sub(r'[^a-zA-Z0-9\s]', '', keyword)

# Function to get Google Trends data with error handling
def get_google_trends(keyword, geo_code):
    pytrends = TrendReq(hl='en-US', tz=360)
    timeframe = 'today 7-d'  # Fixed timeframe for testing
    geo_code = geo_code or "US"  # Default to US if no geo code provided

    try:
        # Sanitize and validate the keyword
        keyword = sanitize_keyword(keyword)
        if not keyword.strip():
            raise ValueError("Keyword must be non-empty and should not contain only whitespace.")

        # Rate limiting to prevent frequent requests
        time.sleep(1)

        # Build the payload with sanitized keyword and geo code
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo_code, gprop='')

        # Fetch interest over time data
        data = pytrends.interest_over_time()

        if data.empty:
            raise ValueError("No data found for the given keyword and location.")
        
        return data
    
    except Exception as e:
        print(f"Error fetching Google Trends data: {e}")
        return None

# Streamlit Interface (For testing on Colab, this might not run directly on Streamlit)
def main():
    st.title('Winning Product Finder Bot with Trend Analysis')

    # Dropdown to select country
    country = st.selectbox("Select a country", list(country_states.keys()))
    country_data = country_states[country]
    country_code = country_data["code"]

    # Optional state selection
    state = st.selectbox("Select a state/province (optional)", ["All"] + list(country_data["states"].keys()))
    state_code = country_data["states"].get(state, None) if state != "All" else country_code

    # Input for product keyword
    keyword = st.text_input("Enter a product keyword (e.g., 'wireless earbuds')")

    # Button to fetch trends and analyze popularity
    if st.button("Find Winning Product"):
        if keyword:
            # Use country or state code for geo
            geo_code = state_code if state_code else country_code

            # Fetch Google Trends data
            trend_data = get_google_trends(keyword, geo_code)
            
            if trend_data is not None and not trend_data.empty:
                # Calculate trend percentage
                trend_data['Percentage'] = (trend_data[keyword] / trend_data[keyword].max()) * 100
                avg_percentage = trend_data['Percentage'].mean()

                # Display trend data
                st.write(f"Trend data for '{keyword}' in {country} ({'state' if state != 'All' else 'country'} level):")
                st.line_chart(trend_data['Percentage'])
                st.write
