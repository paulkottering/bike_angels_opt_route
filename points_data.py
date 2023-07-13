import requests
import json

def get_filtered_bike_stations():
    url = "https://layer.bicyclesharing.net/map/v1/nyc/stations"
    r = requests.get(url)
    data = r.json()
    filtered_data = {"stations": []}

    for feature in data['features']:
        lon, lat = feature['geometry']['coordinates']
        if lat < 40.746411 and lat > 40.711249 and lon < -73.997222 and lon > -74.000639:
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

