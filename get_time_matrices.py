import json
import math
import requests

# Function to calculate distance in km between two points given their coordinates
def calculate_distance(coord1, coord2):
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    return math.sqrt((lon2 - lon1)**2 + (lat2 - lat1)**2) * 111.045

# Define speeds
cycling_speed_kmph = 10
walking_speed_kmph = 3

def get_full_time_matrices():

    url = "https://layer.bicyclesharing.net/map/v1/nyc/stations"
    r = requests.get(url)
    data = r.json()

    filtered_data = {"stations": []}

    for feature in data['features']:
        lon, lat = feature['geometry']['coordinates']
        if lat < 40.846411 and lat > 40.711249 and lon < -73.997222 and lon > -74.300639:
            if 'bike_angels_points' in feature['properties']:  # Check if 'bike_angels_points' exists
                if feature['properties']['renting'] and feature['properties']['returning']:
                    filtered_feature = {
                        "properties": {
                            "coordinates": [lon, lat],
                            "station_id": feature['properties']['station_id'],
                            "name": feature['properties']['name'],
                        }
                    }
                    filtered_data["stations"].append(filtered_feature)

    print(len(filtered_data["stations"]))
    with open('all_bike_stations.json', 'w') as f:
        json.dump(filtered_data, f)

    # Load the data from the JSON file
    with open('all_bike_stations.json') as f:
        data = json.load(f)

    # Create the station ID list
    station_id_list = [station['properties']['station_id'] for station in data['stations']]

    # Create a dictionary for easy access to the coordinates of each station by its ID
    station_coords = {station['properties']['station_id']: station['properties']['coordinates'] for station in data['stations']}

    # Initialize the time matrices
    cycling_time_matrix = {}
    walking_time_matrix = {}

    # Calculate the time taken to travel between each pair of stations
    for id1 in station_id_list:
        cycling_time_matrix[id1] = {}
        walking_time_matrix[id1] = {}
        for id2 in station_id_list:
            distance = calculate_distance(station_coords[id1], station_coords[id2]) # in km
            cycling_time_matrix[id1][id2] = int(60*distance / cycling_speed_kmph+1) # in hours
            walking_time_matrix[id1][id2] = int(60*distance / walking_speed_kmph+1) # in hours

    # Save the matrices to JSON files
    with open('cycling_time_matrix.json', 'w') as f:
        json.dump(cycling_time_matrix, f)

    with open('walking_time_matrix.json', 'w') as f:
        json.dump(walking_time_matrix, f)

# Call the function to generate the time matrices
get_full_time_matrices()
