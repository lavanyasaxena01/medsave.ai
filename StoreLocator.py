import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from urllib.parse import quote

# if st.sidebar.button("💊 Find Medicine"):
#     st.switch_page("main.py")

# if st.sidebar.button("📍 Locate Store"):
#     st.switch_page("pages/StoreLocator.py")

def locatestore():
    st.subheader("Jan Aushadhi Store Locator")

    st.write("Allow location access or search manually by city.")

    but = st.radio(label="Choose an Option",options=["Choose from location","Choose from city"])

    if but == "Choose from location":
    # Get browser location
        location = streamlit_geolocation()
        # -------------------------------
        # CASE 1 : Location Allowed
        # -------------------------------
        if location and location["latitude"] is not None:

            st.write("Location Granted")

            lat = location["latitude"]
            lon = location["longitude"]

            st.success("📍 Current location detected.")

            m = folium.Map(location=[lat, lon], zoom_start=14)

            folium.Marker(
                [lat, lon],
                tooltip="Your Location",
                popup="You are here",
                icon=folium.Icon(color="blue")
            ).add_to(m)

            st_folium(m, width=900, height=500)

            google_url = (
                f"https://www.google.com/maps/search/Jan+Aushadhi/"
                f"@{lat},{lon},15z"
            )

            st.markdown(
                f'<button><a style = "text-decoration:None" href="{google_url}" target="_blank">🔍 Search Nearby Jan Aushadhi Stores</a></button>',
                unsafe_allow_html=True
            )
        else:
            st.warning("Location permission not granted.")


    # -------------------------------
    # CASE 2 : Location Denied
    # -------------------------------
    else:

        st.warning("Location permission not granted.")

        city = st.text_input("Enter your city")

        if st.button("Search by City"):

            if city.strip():

                city_encoded = quote(city.strip())

                google_url = (
                    f"https://www.google.com/maps/search/"
                    f"Jan+Aushadhi+in+{city_encoded}"
                )

                st.markdown(
                    f'<button><a style = "text-decoration:None" href="{google_url}" target="_blank">📍 Open Google Maps</a></button>',
                    unsafe_allow_html=True
                )

                # Optional: Show a map centered on the city
                map_url = (
                    f"https://www.google.com/maps?q={city_encoded}&output=embed"
                )

                st.components.v1.iframe(
                    map_url,
                    height=500,
                    scrolling=False
                )

            else:
                st.error("Please enter a city name.")