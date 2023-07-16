import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Add custom CSS to minimize margins and set max-width for the data table
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 100%;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .dataframe {
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    st.title("Retail and Manufacturing in Madison, WI")
    
    # Add description below the title
    st.markdown("""
    This interactive map displays various retail and manufacturing organizations in Madison, WI. 
    In the left sidebar, the dropdown menus pertaining to organizational type, size, etc. can be filtered. 
    The data table below the interactive map will reflect the filters applied.
    """)

    # Read CSV data from GitHub
    url = 'https://raw.githubusercontent.com/scooter7/simap/main/List1.csv'
    data = pd.read_csv(url)

    # Get the columns (excluding 'Lat' and 'Lon')
    filterable_columns = [col for col in data.columns if col not in ['Lat', 'Lon']]

    # Filter options
    filters = {}
    for col in filterable_columns:
        unique_values = data[col].unique().tolist()
        selected_values = st.sidebar.multiselect(f"Filter by {col}", unique_values)
        filters[col] = selected_values

    # Apply filters
    filtered_data = data.copy()
    for col, values in filters.items():
        if values:
            filtered_data = filtered_data[filtered_data[col].isin(values)]

    # Drop rows with NaN values in latitude and longitude columns
    filtered_data = filtered_data.dropna(subset=['Lat', 'Lon'])

    # Format zip code in the data table
    filtered_data['ZIP'] = filtered_data['ZIP'].astype(str).str.replace(',', '')

    # Create map centered at the mean of latitudes and longitudes
    center_lat = filtered_data['Lat'].mean()
    center_lon = filtered_data['Lon'].mean()
    map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Add markers for each point
    for index, row in filtered_data.iterrows():
        tooltip = f"COMPANY: {row['COMPANY']}\nADDRESS: {row['ADDRESS']}\nZIP: {row['ZIP']}\nCONTACT: {row['CONTACT']}\nEMPLOYEES: {row['EMPLOYEES']}\nSALES: {row['SALES']}\nSIC: {row['SIC']}\nCREDIT: {row['CREDIT']}\nFLEET: {row['FLEET']}"
        folium.Marker([row['Lat'], row['Lon']], tooltip=tooltip).add_to(map)

    # Set up click event to display attribute data
    map.add_child(folium.ClickForMarker(popup=None))

    # Render the map
    st.subheader("Map")
    folium_static(map, width=1000, height=600)

    # Display the filtered data table
    st.subheader("Filtered Data Table")
    st.dataframe(filtered_data)

if __name__ == '__main__':
    main()
