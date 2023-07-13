import json


def get_reduced_matrices():
    # Load all data
    with open('filtered_points_data.json') as f:
        station_data = json.load(f)

    with open('cycling_time_matrix.json') as f:
        cycling_time_data = json.load(f)

    with open('walking_time_matrix.json') as f:
        walking_time_data = json.load(f)

    # Initialize reduced matrices
    times_matrix = {}
    values_matrix = {}

    # Create a station status dictionary for quick lookup
    station_status = {station['properties']['station_id']: station['properties']['bike_angels_action'] for station in
                      station_data['stations']}
    station_points = {station['properties']['station_id']: station['properties']['bike_angels_points'] for station in
                      station_data['stations']}

    # Iterate over all stations
    for id1 in station_data['stations']:
        idx1 = id1['properties']['station_id']
        if idx1 not in times_matrix:
            times_matrix[idx1] = {}
            values_matrix[idx1] = {}

        for id2 in station_data['stations']:
            idx2 = id2['properties']['station_id']

            # Check status of stations
            status1 = station_status[idx1]
            status2 = station_status[idx2]

            if (idx1 not in walking_time_data) and (idx1 not in cycling_time_data):
                print(idx1)
            elif (idx2 not in walking_time_data[idx1]) and (idx2 not in cycling_time_data[idx1]):
                print(idx1,idx2)
            # Fill matrices according to the given rules
            elif status1 == 'give' and status2 in ['take', 'neutral']:
                times_matrix[idx1][idx2] = cycling_time_data[idx1][idx2]
                values_matrix[idx1][idx2] = station_points[idx1] + station_points[idx2]
            elif status1 == 'take' and status2 in ['give', 'neutral']:
                times_matrix[idx1][idx2] = walking_time_data[idx1][idx2]
                values_matrix[idx1][idx2] = 0
            elif status1 == 'neutral':
                if status2 == 'take':
                    times_matrix[idx1][idx2] = cycling_time_data[idx1][idx2]
                    values_matrix[idx1][idx2] = station_points[idx1] + station_points[idx2]
                elif status2 == 'give':
                    times_matrix[idx1][idx2] = walking_time_data[idx1][idx2]
                    values_matrix[idx1][idx2] = 0
                # elif status2 == 'neutral' and idx1 != idx2:
                #     times_matrix[idx1][idx2] = cycling_time_data[idx1][idx2]
                #     values_matrix[idx1][idx2] = station_points[idx1] + station_points[idx2]

    # Save the matrices to JSON files
    with open('reduced_times_matrix.json', 'w') as f:
        json.dump(times_matrix, f)

    with open('reduced_values_matrix.json', 'w') as f:
        json.dump(values_matrix, f)

