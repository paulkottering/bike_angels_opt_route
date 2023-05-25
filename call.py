from get_reduced_matrices import get_reduced_matrices
from dynamic_program import dynamic_program
import json
import requests
import streamlit as st
import pandas as pd

@st.cache(allow_output_mutation=True)
def load_data():
    url = "https://layer.bicyclesharing.net/map/v1/nyc/stations"
    r = requests.get(url)
    data = r.json()
    filtered_data = {"stations": []}

    for feature in data['features']:
        lon, lat = feature['geometry']['coordinates']
        if lat < 40.756411 and lat > 40.711249 and lon < -73.997222 and lon > -74.200639:
            if 'bike_angels_points' in feature['properties']:  # Check if 'bike_angels_points' exists
                if feature['properties']['renting'] and feature['properties']['returning']:
                    filtered_feature = {
                        "properties": {
                            "coordinates": [lon, lat],
                            "station_id": feature['properties']['station_id'],
                            "name": feature['properties']['name'],
                            "bike_angels_points": feature['properties']['bike_angels_points'],
                            "bike_angels_action": feature['properties']['bike_angels_action']
                        }
                    }
                    filtered_data['stations'].append(filtered_feature)

    print(len(filtered_data['stations']))
    with open('filtered_points_data.json', 'w') as f:
        json.dump(filtered_data, f)

    return filtered_data

st.write("Bike Angels")

filtered_data = load_data()

# Create a dictionary mapping station names to their IDs and status
station_dict = {f"{station['properties']['name']} ({station['properties']['bike_angels_action']})":
                station['properties']['station_id']
                for station in filtered_data['stations']}

with st.form(key='stations_form'):
    # Dropdown menu for the start station
    start_station_name = st.selectbox(
        'Select start station:',
        options=list(station_dict.keys()),
        index=0  # Default selection is the first option
    )

    # Dropdown menu for the end station
    end_station_name = st.selectbox(
        'Select end station:',
        options=list(station_dict.keys()),
        index=1  # Default selection is the second option
    )

    T = st.slider('Select maximum cycling time (in minutes):', min_value=0, max_value=60, step=1)

    submit_time_button = st.form_submit_button(label='Submit')

if submit_time_button:
    # Get the IDs of the selected stations
    start_station_id = station_dict[start_station_name]
    end_station_id = station_dict[end_station_name]

    get_reduced_matrices()

    with open('reduced_times_matrix.json') as f:
        times_matrix = json.load(f)

    # Check if the start and end station IDs exist in the matrices
    if start_station_id not in times_matrix or end_station_id not in times_matrix:
        raise ValueError("Start and/or end station ID not found in the matrices")

    with open('filtered_points_data.json') as f:
        bike_stations = json.load(f)

    # Check the status of the start and end stations
    start_status = next((station['properties']['bike_angels_action'] for station in bike_stations['stations'] if
                         station['properties']['station_id'] == start_station_id), None)
    end_status = next((station['properties']['bike_angels_action'] for station in bike_stations['stations'] if
                       station['properties']['station_id'] == end_station_id), None)

    if start_status not in ['take', 'neutral'] or end_status not in ['give', 'neutral']:
        print(start_status)
        print(end_status)
        raise ValueError("Status of start and end stations is incorrect")

    # Check if the cycling time between the start and end stations is less than T
    cycling_time = times_matrix[end_station_id][start_station_id]
    st.write(f"The direct cycling time between the start and end stations is {cycling_time} minutes.")


    start_station_name = next((station['properties']['name'] for station in bike_stations['stations'] if
                               station['properties']['station_id'] == start_station_id), None)
    end_station_name = next((station['properties']['name'] for station in bike_stations['stations'] if
                             station['properties']['station_id'] == end_station_id), None)

    print(f"Beginning station: {start_station_name}")
    print(f"End station: {end_station_name}")

    # Call the function with the selected stations
    path = dynamic_program(start_station_id, end_station_id, T)

    # Create a list of dictionaries for the table
    table_data = []
    for step in path:
        row = {
            'From Station': step['from_station'],
            'To Station': step['to_station'],
            'Time (minutes)': step['time'],
            'Mode': step['mode'],
            'Points': step['points'],
        }
        table_data.append(row)

    # Display the table
    st.table(table_data)

    # Create a DataFrame for the map
    map_data = pd.DataFrame({
        'lat': [step['from_station_lat'] for step in path] + [step['to_station_lat'] for step in path],
        'lon': [step['from_station_lon'] for step in path] + [step['to_station_lon'] for step in path],
    })

    # Display the map
    st.map(map_data)