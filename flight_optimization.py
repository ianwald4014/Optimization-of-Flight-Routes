#! /usr/bin/env python3

import numpy as np
import scipy.integrate as integrate
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2

def parse_flight_data_initial(lines):
    flight_data = {}
    flight_number = None
    for line in lines:
        if line.startswith("Flight:"):
            flight_number = int(line.split(":")[1].strip())
            flight_data[flight_number] = {}
        elif line.startswith("Flight Path:"):
            flight_data[flight_number]['flight_path'] = line.split(":")[1].strip()
        elif line.startswith("Origin:"):
            flight_data[flight_number]['origin'] = line.split(":")[1].strip().split()[0]
        elif line.startswith("Origin Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['origin_coordinates'] = (float(coords[0]), float(coords[1]))
        elif line.startswith("Destination:"):
            flight_data[flight_number]['destination'] = line.split(":")[1].strip().split()[0]
        elif line.startswith("Destination Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['destination_coordinates'] = (float(coords[0]), float(coords[1]))
        elif line.startswith("Stops:"):
            flight_data[flight_number]['stops'] = int(line.split(":")[1].strip())
        elif line.startswith("Stop1:"):
            stop1 = line.split(":")[1].strip().split()[0]
            if stop1 != "None":
                flight_data[flight_number]['stop1'] = stop1
        elif line.startswith("Stop1 Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['stop1_coordinates'] = (float(coords[0]), float(coords[1]))
        elif line.startswith("Stop2:"):
            stop2 = line.split(":")[1].strip().split()[0]
            if stop2 != "None":
                flight_data[flight_number]['stop2'] = stop2
        elif line.startswith("Stop2 Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['stop2_coordinates'] = (float(coords[0]), float(coords[1]))
        elif line.startswith("Passengers:"):
            flight_data[flight_number]['passengers'] = int(line.split(":")[1].strip())
        elif line.startswith("Distance (Nautical Miles):"):
            flight_data[flight_number]['distance_nm'] = float(line.split(":")[1].strip())
        elif line.startswith("Flight Time (Hours):"):
            flight_data[flight_number]['flight_time'] = float(line.split(":")[1].strip())
        elif line.startswith("Operating Cost:"):
            flight_data[flight_number]['operational_cost'] = float(line.split(": $")[1].strip())
        elif line.startswith("Layover Time (Hours):"):
            flight_data[flight_number]['layover_time'] = float(line.split(":")[1].strip())
        elif line.startswith("Maintenance Cost:"):
            flight_data[flight_number]['maintenance_cost'] = float(line.split(": $")[1].strip())
        elif line.startswith("Income of Flight:"):
            flight_data[flight_number]['flight_income'] = float(line.split(": $")[1].strip())
        elif line.startswith("Net Profit of the Flight:"):
            flight_data[flight_number]['net_profit'] = float(line.split(": $")[1].strip())
        elif line.startswith("Note: This flight has been revised"):
            flight_data[flight_number]['revised'] = True
        elif line.startswith("Total Passenger Miles:"):
            continue

    return list(flight_data.values())

def get_worst_flights_by_profit(flight_data, num_worst=3):
    profits = [(i, flight_info['net_profit']) for i, flight_info in enumerate(flight_data)]
    sorted_profits = sorted(profits, key=lambda x: x[1])
    return sorted_profits[:num_worst]

def haversine(coord1, coord2):
    R = 3440.065  # Radius of the Earth in nautical miles
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def calculate_distances(data):
    origin_coords = data['origin_coordinates']
    destination_coords = data['destination_coordinates']
    
    stops = [data.get('stop1_coordinates'), data.get('stop2_coordinates')]
    num_stops = data['stops']
    
    distances = {}
    segments = []

    # Calculate distances for each segment
    if num_stops == 0:
        segments.append(('origin_to_destination', origin_coords, destination_coords))
    elif num_stops == 1:
        if stops[0] is not None:
            segments.append(('origin_to_stop1', origin_coords, stops[0]))
            segments.append(('stop1_to_destination', stops[0], destination_coords))
        else:
            raise ValueError("Insufficient data to calculate distance with 1 stop.")
    elif num_stops == 2:
        if stops[0] is not None and stops[1] is not None:
            segments.append(('origin_to_stop1', origin_coords, stops[0]))
            segments.append(('stop1_to_stop2', stops[0], stops[1]))
            segments.append(('stop2_to_destination', stops[1], destination_coords))
        else:
            raise ValueError("Insufficient data to calculate distance with 2 stops.")
    else:
        raise ValueError("Invalid number of stops. Only 0, 1, or 2 stops are supported.")
    
    # Compute distances for each segment
    total_distance = 0
    for label, start_coords, end_coords in segments:
        distance = haversine(start_coords, end_coords)
        distances[label] = distance
        total_distance += distance

    return total_distance

def calculate_proximity_score(base_flight, candidate_flight):
    def extract_coordinates(flight):
        coordinates = [
            flight['origin_coordinates'],
            flight.get('stop1_coordinates', None),
            flight.get('stop2_coordinates', None),
            flight['destination_coordinates']
        ]
        return [coord for coord in coordinates if coord is not None]

    coords_base = extract_coordinates(base_flight)
    coords_candidate = extract_coordinates(candidate_flight)

    min_distances = []

    for coord_base in coords_base:
        min_distance = float('inf')
        for coord_candidate in coords_candidate:
            distance = haversine(coord_base, coord_candidate)
            if distance < min_distance:
                min_distance = distance
        min_distances.append(min_distance)
    
    # Calculate the average of minimum distances
    average_distance = np.mean(min_distances)
    
    # Convert distance to score (inverse of the distance, scaled to positive range)
    # Add a small constant to avoid division by zero if average_distance is zero
    score = 1 / (average_distance + 1e-6)
    
    return score

def find_best_candidates(flight_data, base_flight_index, num_candidates=10, scoring_method='average'):
    base_flight = flight_data[base_flight_index]
    candidates = []

    for index, candidate_flight in enumerate(flight_data):
        if index != base_flight_index:
            if scoring_method == 'average':
                distance_score = calculate_proximity_score(base_flight, candidate_flight)
                candidates.append((index, distance_score))
    
    # Sort candidates by distance score and select the top ones
    candidates.sort(key=lambda x: x[1], reverse=True)  # Higher score is better
    return candidates[:num_candidates]

def specialized_candidate(flight_data, base_flight_index, candidate_indices):
    base_flight = flight_data[base_flight_index]
    specialized_candidate_index = None
    best_candidate_score = -float('inf')  # Initialize to negative infinity for comparison
    
    # Retrieve the base flight data
    base_passengers = base_flight.get('passengers', 0)
    base_net_profit = base_flight.get('net_profit', 0)
    base_passenger_miles = base_flight.get('total_passenger_miles', 0)
    
    # Iterate through candidate flight indices
    for candidate_index in candidate_indices:
        candidate_flight = flight_data[candidate_index]
        candidate_passengers = candidate_flight.get('passengers', 0)
        candidate_net_profit = candidate_flight.get('net_profit', 0)
        candidate_passenger_miles = candidate_flight.get('total_passenger_miles', 0)
        candidate_proximity_score = calculate_proximity_score(base_flight, candidate_flight)
        
        # Check if the combined number of passengers is less than or equal to 204
        if base_passengers + candidate_passengers <= 204:
            # Compute a combined score considering net profit, passenger miles, and proximity score
            combined_score = (candidate_net_profit + candidate_passenger_miles + candidate_proximity_score)
            
            # Check if this candidate is better
            if combined_score > best_candidate_score:
                best_candidate_score = combined_score
                specialized_candidate_index = candidate_index

    return specialized_candidate_index

def path_modified(bad_flight, candidate_flight):
    # Extract and split the stops from both flights, handling None values
    bad_stops = [stop for stop in [bad_flight['origin'], bad_flight.get('stop1', None), bad_flight.get('stop2', None), bad_flight['destination']] if stop is not None]
    candidate_stops = [stop for stop in [candidate_flight['origin'], candidate_flight.get('stop1', None), candidate_flight.get('stop2', None), candidate_flight['destination']] if stop is not None]
    
    # Convert lists to strings for merging
    bad_path_str = ' , '.join(bad_stops)
    candidate_path_str = ' , '.join(candidate_stops)
    
    # Merge the paths: candidate origin + candidate stops + bad flight stops + candidate destination
    new_path_str = f"{candidate_path_str} , {bad_path_str}"
    
    # Split the merged path into a list of stops
    new_path_list = new_path_str.split(' , ')
    
    # Remove duplicates while preserving order
    seen = set()
    new_path_filtered = [x for x in new_path_list if not (x in seen or seen.add(x))]
    
    return ' , '.join(new_path_filtered)

def best_candidate_merge(flight_data, flight_index, candidates):
    base_flight = flight_data[flight_index]
    specialized_candidate_index = None
    best_candidate_index = None

    for candidate_index, _ in candidates:
        candidate = flight_data[candidate_index]
        valid_merge, new_distance_nm, new_passenger_miles, new_oper_cost, new_income, combined_passengers, new_net_profit = updated_variables(base_flight, candidate)
        
        if valid_merge and new_net_profit > base_flight['net_profit']:
            best_candidate_index = candidate_index
            
            # Get the new path by merging base flight's stops into the candidate flight's path
            new_path = path_modified(base_flight, candidate)
            
            # Update the base flight's data with the new values
            flight_data[flight_index].update({
                'distance_nm': new_distance_nm,
                'total_passenger_miles': new_passenger_miles,
                'operational_cost': new_oper_cost,
                'flight_income': new_income,
                'passengers': combined_passengers,
                'net_profit': new_net_profit,
                'revised_flight_path': new_path,  # Set the revised flight path here
                'revised': True
            })
            
            # Set the specialized candidate index to the best candidate index
            specialized_candidate_index = candidate_index
            
            # Remove the old base flight (bad flight) from the list
            flight_data.pop(flight_index)
            break
    
    return specialized_candidate_index

def count_stops(flight_path):
    # Split the flight path into individual airport codes
    airports = flight_path.split(' , ')
    
    # The first and last elements are origin and destination
    origin = airports[0]
    destination = airports[-1]
    
    # Count the number of stops (excluding origin and destination)
    stops = airports[1:-1]
    
    return len(stops), stops

def calculate_flight_time(lon1, lat1, lon2, lat2): # Refer back to the generation of flights
    if None in [lat1, lon1, lat2, lon2]:
        return 0, 0  # Handle invalid coordinates
    distance_nm = haversine_distance_nm(lat1, lon1, lat2, lon2)
    speed_knots = 485  # Average speed of a Boeing 737 MAX in knots
    flight_time = distance_nm / speed_knots
    operational_cost = 5757 * flight_time
    return flight_time, operational_cost

def simulate_layover(stops, flight_time, operational_cost):
    """Simulate layover time and calculate maintenance cost."""
    if stops == 0:
        layover_time = 0
        maintenance_cost = operational_cost
    else:
        layover_time = 1.5 * stops  # Layover time in hours
        maintenance_cost_per_hour = 150  # Maintenance cost per hour
        maintenance_cost = (layover_time * maintenance_cost_per_hour) + operational_cost
    
    return layover_time, maintenance_cost

def update_statistics(flight_data, flight_index):
    data = flight_data[flight_index]

    # Get the revised flight path dynamically
    origin = data.get('origin')
    destination = data.get('destination')
    stops = [data.get(f'stop{i+1}', 'None') for i in range(6) if data.get(f'stop{i+1}', 'None') != 'None']
    flight_path = [origin] + stops + [destination]

    # Retrieve coordinates for each stop
    stops_coords = [data['origin_coordinates']]
    for stop in stops:
        stop_key = f"{stop.lower()}_coordinates"
        if stop_key in data:
            stops_coords.append(data[stop_key])
    stops_coords.append(data['destination_coordinates'])

    # Calculate total flight distance, time, and operational cost
    total_distance_nm = 0
    total_flight_time = 0
    total_operational_cost = 0

    for i in range(len(stops_coords) - 1):
        coord1 = stops_coords[i]
        coord2 = stops_coords[i + 1]
        if coord1 and coord2:
            flight_time, operational_cost, distance_nm = calculate_flight_time(
                coord1[1], coord1[0], coord2[1], coord2[0]
            )
            total_distance_nm += distance_nm
            total_flight_time += flight_time
            total_operational_cost += operational_cost

    # Update flight data with calculated values
    data['flight_time'] = total_flight_time
    data['operating_cost'] = total_operational_cost
    data['distance_nm'] = total_distance_nm

    # Simulate layover and calculate maintenance cost
    num_stops = len(stops)
    layover_time, maintenance_cost = simulate_layover(num_stops, total_flight_time, total_operational_cost)
    data['layover_time'] = layover_time
    data['maintenance_cost'] = maintenance_cost

    # Calculate flight income
    passengers = data.get('passengers', 0)
    flight_income = 384.85 * passengers
    data['flight_income'] = flight_income

    # Calculate the net profit
    net_profit = flight_income - maintenance_cost - total_operational_cost
    data['net_profit'] = net_profit

    # Calculate total passenger miles
    passenger_miles = passengers * total_distance_nm
    data['total_passenger_miles'] = passenger_miles

    return flight_data

def process_flight_data(flight_data, base_flight_index, num_candidates=10): # Sequence the process
    # Step 1: Find the best candidates based on proximity score
    candidates = find_best_candidates(flight_data, base_flight_index, num_candidates)
    
    # Step 2: Identify the specialized candidate
    candidate_indices = [index for index, score in candidates]
    specialized_candidate_index = specialized_candidate(flight_data, base_flight_index, candidate_indices)
    
    # Step 3: Merge the best candidate
    if specialized_candidate_index is not None:
        merged_flight_index = best_candidate_merge(flight_data, base_flight_index, candidates)
        if merged_flight_index is not None:
            # Step 4: Update the statistics of the merged flight
            flight_data = update_statistics(flight_data, merged_flight_index)
    
    return flight_data

def main(scoring_method: str = 'average') -> None:
    input_file = "sorted_flights.txt"
    output_file = "modified_flights_final.txt"

    try:
        with open(input_file, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Input file {input_file} not found.")
        return

    flight_data = parse_flight_data_initial(lines)
    optimized_flights = set()

    iteration = 0
    while True:
        print(f"\nIteration {iteration + 1}: Optimizing flights...")

        # Identify and process the worst flights
        worst_flights = get_worst_flights_by_profit(flight_data, num_worst=3)

        if not worst_flights:
            print("No more flights to optimize.")
            break

        for flight in worst_flights:
            flight_index, profit = flight
            if flight_index in optimized_flights:
                continue  # Skip flights that have already been optimized

            print(f"\nProcessing Flight {flight_index}: Profit ${profit:.2f}")

            path_non_modified = ", ".join([
                str(flight_data[flight_index]['origin']),
                *([str(flight_data[flight_index].get(f'stop{i+1}', 'None')) for i in range(2)]),
                str(flight_data[flight_index]['destination'])
            ])
            print(f"Non-Modified Flight Path: {path_non_modified}")

            path_modified = ", ".join([
                str(flight_data[flight_index]['origin']),
                *([str(flight_data[flight_index].get(f'stop{i+1}', 'None')) for i in range(6)]),
                str(flight_data[flight_index]['destination'])
            ])
            print(f"Modified Flight Path: {path_modified}")

            candidates = find_best_candidates(flight_data, flight_index, scoring_method=scoring_method)

            print(f"\nPotentially optimal flights for merging with Flight {flight_index}:")
            for candidate_index, distance in candidates:
                print(f"Candidate Flight {candidate_index}: Distance {distance:.2f} NM")

            best_candidate_index = None
            for candidate_index, _ in candidates:
                candidate = flight_data[candidate_index]
                valid_merge, new_distance_nm, new_passenger_miles, new_oper_cost, new_income, combined_passengers, new_net_profit = updated_variables(flight_data[flight_index], candidate)
                if valid_merge and new_net_profit > flight_data[flight_index]['net_profit']:
                    best_candidate_index = candidate_index
                    flight_data[flight_index].update({
                        'distance_nm': new_distance_nm,
                        'total_passenger_miles': new_passenger_miles,
                        'operational_cost': new_oper_cost,
                        'flight_income': new_income,
                        'passengers': combined_passengers,
                        'net_profit': new_net_profit,
                        'revised_flight_path': path_modified,
                        'revised': True
                    })
                    break

            if best_candidate_index is not None:
                print(f"\nBest candidate for merging with Flight {flight_index} is Flight {best_candidate_index}")
                print(f"Modified Flight Route of Flight {flight_index}: {flight_data[flight_index].get('revised_flight_path')}\n")
                optimized_flights.add(flight_index)
            else:
                print(f"\nNo suitable candidate found for merging with Flight {flight_index}.\n")

        # Check if all flights have been optimized
        if len(optimized_flights) == len(flight_data):
            print("All flights have been optimized.")
            break

        iteration += 1

    # Write the final optimized flight data to file
    try:
        with open(output_file, "w") as file:
            for flight_number, data in enumerate(flight_data):
                file.write(f"Flight: {flight_number}\n")
                file.write(f"Flight Path: {data.get('revised_flight_path', '')}\n")
                file.write(f"Origin: {data.get('origin', '')}\n")
                file.write(f"Origin Coordinates: {data['origin_coordinates'][0]},{data['origin_coordinates'][1]}\n")
                file.write(f"Destination: {data.get('destination', 'None')}\n")
                file.write(f"Destination Coordinates: {data['destination_coordinates'][0]},{data['destination_coordinates'][1]}\n")
                
                for i in range(1, 7):
                    stop_key = f'stop{i}'
                    stop_coords_key = f'stop{i}_coordinates'
                    stop = data.get(stop_key, 'None')
                    stop_coords = data.get(stop_coords_key, (0, 0))
                    file.write(f"Stop{i}: {stop}\n")
                    if stop != 'None':
                        file.write(f"Stop{i} Coordinates: {stop_coords[0]},{stop_coords[1]}\n")
                    else:
                        file.write(f"Stop{i} Coordinates: None\n")

                file.write(f"Passengers: {data.get('passengers', 0)}\n")
                file.write(f"Distance (Nautical Miles): {data.get('distance_nm', 0):.2f}\n")
                file.write(f"Flight Time (Hours): {data.get('flight_time', 0):.2f}\n")
                file.write(f"Operating Cost: ${data.get('operational_cost', 0):.2f}\n")
                file.write(f"Layover Time (Hours): {data.get('layover_time', 0):.2f}\n")
                file.write(f"Maintenance Cost: ${data.get('maintenance_cost', 0):.2f}\n")
                file.write(f"Income of Flight: ${data.get('flight_income', 0):.2f}\n")
                file.write(f"Net Profit of the Flight: ${data.get('net_profit', 0):.2f}\n")
                file.write(f"Total Passenger Miles: {data.get('total_passenger_miles', 0):.2f} passenger miles.\n")
                file.write("\n")

            if any(flight.get('revised', False) for flight in flight_data):
                file.write("Note: Some flights have been revised.\n")
                file.write("\n")

    except IOError:
        print(f"Error writing to file {output_file}.")

if __name__ == "__main__":
    main(scoring_method='average')
