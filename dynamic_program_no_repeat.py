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

def get_station_mode(id):
    with open('filtered_points_data.json') as f:
        bike_stations = json.load(f)
    return bike_stations['stations'][id]['properties']['bike_angels_action']

def dynamic_program_no_repeat(start_station_id, end_station_id, T):
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

    visited_list = [[[] for _ in range(T)] for _ in range(num_nodes)]

    # Get the indices of the start and end stations
    start_index = station_ids.index(start_station_id)
    end_index = station_ids.index(end_station_id)

    djt[start_index, 0] = 0

    visited_list[start_index][0].append(start_index)

    connections = {i: [j for j in range(num_nodes) if station_ids[j] in times_matrix[station_ids[i]]] for i in range(num_nodes)}

    # Main loop of the dynamic programming algorithm
    # This loop goes over each time unit from 1 to the total time allowed
    for t in range(1, T):
        # For each time unit, it iterates over all the stations
        for j in range(num_nodes):
            # Initialize variables m and temp_k which store the max value found in this iteration and the index of the station which gives this max value
            m = -np.inf
            temp_k = -np.inf
            # Iterate over all the stations connected to the current station j
            for i in connections[j]:
                # Assign the index of the current connected station to k
                k = i
                # Get the points for moving from station j to station k
                p_kj = values_matrix[station_ids[j]][station_ids[k]]
                # Get the time for moving from station j to station k
                t_kj = times_matrix[station_ids[j]][station_ids[k]]
                # Check if the time for moving from station j to station k is less than or equal to the current time unit
                if t - t_kj >= 0:
                    # If it is, check if the total points for moving from station j to station k plus the points accumulated till the previous time unit at station k is greater than the max value found so far
                    if djt[k, t - t_kj] + p_kj > m:
                        if j not in visited_list[k][t - t_kj]:
                            # If it is, update the max value and the index of the station which gives this max value
                            m = djt[k, t - t_kj] + p_kj
                            temp_k = k

            # After checking all connected stations, check if the points accumulated at station j in the previous time unit is greater than the max value found in this iteration
            if djt[j, t - 1] > m:
                # If it is, the best move for this time unit at station j is to stay put, so assign the points and the station from the previous time unit
                djt[j, t] = djt[j, t - 1]
                dir_jt[j, t] = dir_jt[j, t - 1]
                visited_list[j][t] = visited_list[j][t - 1].copy()

            elif djt[j, t - 1] == m and not np.isinf(temp_k):
                t_kj = times_matrix[station_ids[j]][station_ids[temp_k]]
                if len(visited_list[j][t - 1]) < (len(visited_list[temp_k][t - t_kj]) + 1):
                    print('ha')
                    djt[j, t] = djt[j, t - 1]
                    dir_jt[j, t] = dir_jt[j, t - 1]
                    visited_list[j][t] = visited_list[j][t - 1].copy()
                else:
                    djt[j, t] = m
                    dir_jt[j, t] = temp_k

                    t_kj = times_matrix[station_ids[j]][station_ids[temp_k]]
                    visited_list[j][t] = visited_list[temp_k][t - t_kj].copy()
                    visited_list[j][t].append(j)

            elif not np.isinf(temp_k) and (djt[j, t - 1] < m):
                # If it's not, the best move for this time unit at station j is to have come from station which gives the max value, so assign the max value and the station index
                djt[j, t] = m
                dir_jt[j, t] = temp_k

                t_kj = times_matrix[station_ids[j]][station_ids[temp_k]]
                visited_list[j][t] = visited_list[temp_k][t - t_kj].copy()
                visited_list[j][t].append(j)

    current_node = end_index
    current_time = T - 1


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
                'from_station_mode': get_station_mode(int(next_node)),
                'to_station_mode': get_station_mode(int(current_node)),
                'to_station_lat': station_coordinates[1],
                'to_station_lon': station_coordinates[0],
            })

            total_points += points
            current_time -= time_to_get_to_next_node
        else:
            break

        current_node = next_node

    return reversed(path),total_points


