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

    # Define the custom order for EMPLOYEES
    employees_order = [
        '5 to 9',
        '10 to 19',
        '20 to 49',
        '50 to 99',
        '100 to 249',
        '250 to 499',
        '500 to 999',
        '1000 to 4999',
        '5000 to 9999'
    ]

    # Define the custom order for SALES
    sales_order = [
        '$20 - 50 MILLION',
        '$50 - 100 MILLION',
        '$100 - 500 MILLION',
        '$500 MILLION - $1 BILLION',
        'OVER $1 BILLION'
    ]

    # Define the custom order for CREDIT
    credit_order = ['I', 'B', 'B+', 'A', 'A+']

    # Define the custom order for ZIP
    zip_order = sorted(data['ZIP'].unique())

    # Define the custom order for FLEET
    fleet_order = [
        'Unknown',
        '1 to 10',
        '11 to 19',
        '20 to 49',
        '50+',
        '50 to 99'
    ]

    # Get the columns (excluding 'Lat' and 'Lon') and remove 'CITY' and 'STATE'
    filterable_columns = [col for col in data.columns if col not in ['Lat', 'Lon', 'CITY', 'STATE']]

    # Filter options
    filters = {}
    for col in filterable_columns:
        unique_values = data[col].unique().tolist()

        # Apply custom order to the filter options
        if col == 'EMPLOYEES':
            unique_values = sorted(unique_values, key=lambda x: employees_order.index(x))
        elif col == 'SALES':
            unique_values = sorted(unique_values, key=lambda x: sales_order.index(x))
        elif col == 'CREDIT':
            unique_values = sorted(unique_values, key=lambda x: credit_order.index(x))
        elif col == 'ZIP':
            unique_values = sorted(unique_values, key=lambda x: zip_order.index(x))
        elif col == 'FLEET':
            unique_values = sorted(unique_values, key=lambda x: fleet_order.index(x))

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
        tooltip = f"""
        <b>COMPANY:</b> {row['COMPANY']}<br>
        <b>ADDRESS:</b> {row['ADDRESS']}<br>
        <b>ZIP:</b> {row['ZIP']}<br>
        <b>CONTACT:</b> {row['CONTACT']}<br>
        <b>EMPLOYEES:</b> {row['EMPLOYEES']}<br>
        <b>SALES:</b> {row['SALES']}<br>
        <b>SIC:</b> {row['SIC']}<br>
        <b>CREDIT:</b> {row['CREDIT']}<br>
        <b>FLEET:</b> {row['FLEET']}
        """
        folium.Marker([row['Lat'], row['Lon']], tooltip=tooltip, parse_html=True).add_to(map)

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
