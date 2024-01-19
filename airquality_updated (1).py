import streamlit as st
import requests
from geopy.geocoders import Nominatim
import plotly.express as px
import pycountry 

# Function to update coordinates and API key in the URL
def update_coordinates_and_api_key(url, latitude, longitude, api_key):
    if "{LATITUDE}" in url and "{LONGITUDE}" in url and "{YOUR_API_KEY}" in url:
        url = url.replace("{LATITUDE}", str(latitude)).replace("{LONGITUDE}", str(longitude)).replace("{YOUR_API_KEY}", api_key)
        return url
    else:
        st.error("Error: The URL does not contain placeholders for latitude, longitude, and/or API key.")
        return None

# Function to get the air quality index for a given city
def get_air_quality(latitude, longitude, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/air_pollution?lat={LATITUDE}&lon={LONGITUDE}&appid={YOUR_API_KEY}"
    url = update_coordinates_and_api_key(base_url, latitude, longitude, api_key)

    if url:
        response = requests.get(url)
        data = response.json()
        return data['list'][0]['main']['aqi'], data['list'][0]['components']
    else:
        return None, None

# Function to map AQI to qualitative names based on pollutant concentration
def map_aqi_to_condition(aqi, pollutants):
    if aqi == 1:
        return "Good"
    elif aqi == 2:
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4:
        return "Poor"
    elif aqi == 5:
        return "Very Poor"
    else:
        return "Unknown"

# Streamlit app

def get_all_countries():
    return [country.name for country in pycountry.countries]

def get_cities_in_country(country):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(country)
    if location:
        address = location.address.split(", ")
        return address[-3:]
    else:
        return []


def main():
    
    st.title("Air Quality Index Checker")
    city_name = st.text_input("Enter the name of the city:")
    

    

    # Get coordinates and API key for the selected city
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(city_name)
    latitude = location.latitude
    longitude = location.longitude
    api_key = "0e6749162b11f1ad936dd59feb1e7732"  

    # Get air quality index and pollutant components
    air_quality_index, pollutant_components = get_air_quality(latitude, longitude, api_key)

    # Map AQI to qualitative names based on pollutant concentration
    weather_condition = map_aqi_to_condition(air_quality_index, pollutant_components)

    # Display the result
    if air_quality_index is not None:
        st.write(f"The Air Quality Index (AQI) in {city_name} is: {air_quality_index}")
        st.write(f"The weather condition is: {weather_condition}")

        # Create a pie chart for pollutant distribution
        fig = px.pie(
            values=list(pollutant_components.values()),
            names=list(pollutant_components.keys()),
            title=f'Pollutant Distribution in {city_name}'
        )
        st.plotly_chart(fig)

    else:
        st.error("Failed to retrieve air quality information.")

if __name__ == "__main__":
    main()
