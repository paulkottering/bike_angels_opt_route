import json
import numpy as np

def get_mode(from_id,to_id):
    with open('filtered_points_data.json') as f:
        bike_stations = json.load(f)
    from_status = bike_stations['stations'][from_id]['properties']['bike_angels_action']
    to_status = bike_stations['stations'][to_id]['properties']['bike_angels_action']

    if from_status == 'take':
        return 'cycle'
    if from_status == 'give':
        return 'walk'
    elif to_status == 'take':
        return 'walk'
    elif to_status == 'give':
        return 'cycle'
    else:
        return 'cycle'

def dynamic_program(start_station_id, end_station_id, T):
    # Load reduced matrices
    with open('reduced_times_matrix.json') as f:
        times_matrix = json.load(f)

    with open('reduced_values_matrix.json') as f:
        values_matrix = json.load(f)

    with open('filtered_points_data.json') as f:
        bike_stations = json.load(f)

    # Get the list of station IDs
    station_ids = list(times_matrix.keys())
    num_nodes = len(station_ids)

    # Initialize the dynamic programming table and direction table
    djt = np.ones((num_nodes, T)) * (-np.inf)
    dir_jt = np.ones((num_nodes, T)) * (-np.inf)

    # Get the indices of the start and end stations
    start_index = station_ids.index(start_station_id)
    end_index = station_ids.index(end_station_id)

    djt[start_index, 0] = 0

    connections = {i: [j for j in range(num_nodes) if station_ids[j] in times_matrix[station_ids[i]]] for i in range(num_nodes)}

    # Main loop of the dynamic programming algorithm
    for t in range(1, T):
        for j in range(num_nodes):
            m = -np.inf
            temp_k = -np.inf
            for i in connections[j]:
                k = i
                p_kj = values_matrix[station_ids[j]][station_ids[k]]
                t_kj = times_matrix[station_ids[j]][station_ids[k]]

                if t-t_kj >= 0:
                    if djt[k, t-t_kj] + p_kj > m:
                        m = djt[k, t-t_kj] + p_kj
                        temp_k = k

            if djt[j, t-1] > m:
                djt[j, t] = djt[j, t-1]
                dir_jt[j, t] = dir_jt[j, t-1]
            else:
                djt[j, t] = m
                dir_jt[j, t] = temp_k

    current_node = end_index
    current_time = T - 1

    print(djt[end_index,T-1])

    path = []
    total_points = 0

    while current_time > 0:
        next_node = dir_jt[int(current_node)][current_time]

        if next_node == -np.inf:
            break

        station = next((station for station in bike_stations['stations'] if
                        station['properties']['station_id'] == station_ids[int(current_node)]), None)
        station_name = station['properties']['name']
        station_coordinates = station['properties']['coordinates']
        time_to_get_to_next_node = times_matrix[station_ids[int(current_node)]][station_ids[int(next_node)]]
        points = values_matrix[station_ids[int(current_node)]][station_ids[int(next_node)]]

        if time_to_get_to_next_node <= current_time:
            next_station = next((station for station in bike_stations['stations'] if
                                 station['properties']['station_id'] == station_ids[int(next_node)]), None)
            next_station_name = next_station['properties']['name']
            next_station_coordinates = next_station['properties']['coordinates']
            path.append({
                'from_station': next_station_name,
                'to_station': station_name,
                'time': time_to_get_to_next_node,
                'points': points,
                'mode': get_mode(int(next_node),int(current_node)),
                'from_station_lat': next_station_coordinates[1],
                'from_station_lon': next_station_coordinates[0],
                'to_station_lat': station_coordinates[1],
                'to_station_lon': station_coordinates[0],
            })

            total_points += points
            current_time -= time_to_get_to_next_node
        else:
            break

        current_node = next_node

    return reversed(path)