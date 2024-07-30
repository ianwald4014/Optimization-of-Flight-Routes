#! /usr/bin/env python3

import time
import numpy as np
import scipy.integrate as integrate
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2

def parse_flight_data_initial(lines):
    flight_data = {}
    flight_number = None
    current_lines = []
    
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace
        
        if line.startswith("Flight:"):
            # Save previous flight data if it exists
            if flight_number is not None:
                flight_data[flight_number]['lines'] = current_lines
            
            # Start a new flight entry
            flight_number = int(line.split(":")[1].strip())
            flight_data[flight_number] = {}
            current_lines = [line]
        
        else:
            # Append line to the current flight's lines
            if flight_number is not None:
                current_lines.append(line)
                
                if line.startswith("Flight Path:"):
                    flight_data[flight_number]['flight_path'] = line.split(":")[1].strip()
                elif line.startswith("Origin:"):
                    flight_data[flight_number]['origin'] = line.split(":")[1].strip()
                elif line.startswith("Origin Coordinates:"):
                    coords = line.split(":")[1].strip().split(",")
                    flight_data[flight_number]['origin_coordinates'] = (float(coords[0]), float(coords[1]))
                elif line.startswith("Destination:"):
                    flight_data[flight_number]['destination'] = line.split(":")[1].strip()
                elif line.startswith("Destination Coordinates:"):
                    coords = line.split(":")[1].strip().split(",")
                    flight_data[flight_number]['destination_coordinates'] = (float(coords[0]), float(coords[1]))
                elif line.startswith("Stops:"):
                    flight_data[flight_number]['stops'] = int(line.split(":")[1].strip())
                elif line.startswith("Stop1:"):
                    stop1 = line.split(":")[1].strip()
                    if stop1 != "None":
                        flight_data[flight_number]['stop1'] = stop1
                elif line.startswith("Stop1 Coordinates:"):
                    coords = line.split(":")[1].strip().split(",")
                    flight_data[flight_number]['stop1_coordinates'] = (float(coords[0]), float(coords[1]))
                elif line.startswith("Stop2:"):
                    stop2 = line.split(":")[1].strip()
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
                    net_profit_str = line.split(": $")[1].strip()
                    try:
                        flight_data[flight_number]['net_profit'] = float(net_profit_str)
                    except ValueError:
                        print(f"Error parsing net profit '{net_profit_str}' for flight {flight_number}")
                        flight_data[flight_number]['net_profit'] = None
                elif line.startswith("Total Passenger Miles:"):
                    continue  # Skip or handle if needed
    
    # Don't forget to save the last flight's data
    if flight_number is not None:
        flight_data[flight_number]['lines'] = current_lines
    
    return list(flight_data.values())

def optimize_flights(flight_data, profit_threshold):
    # Extract profits and filter flights with profits below the threshold
    profits = [(i, flight_info['net_profit']) for i, flight_info in enumerate(flight_data)]
    worst_flights = [(i, profit) for i, profit in profits if profit < profit_threshold]
    
    # Count the number of bad flights
    num_bad_flights = len(worst_flights)
    print(f"Number of bad flights with profit below ${profit_threshold}: {num_bad_flights}")
    
    # Sort the worst flights by profit in ascending order (more negative profits come first)
    worst_flights_sorted = sorted(worst_flights, key=lambda x: x[1])
    
    # Print the worst flights and their profits
    print("\nWorst Flights and Their Profits:")
    for flight_index, profit in worst_flights_sorted:
        print(f"Flight {flight_index}: Profit ${profit:,.2f}")

    # Process only the flights listed in worst_flights_sorted
    for flight_index, _ in worst_flights_sorted:
        flight_data = process_bad_flight(flight_data, flight_index, profit_threshold)

    return flight_data

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

    if num_stops == 0:
        segments.append(('origin_to_destination', origin_coords, destination_coords))
    elif num_stops == 1:
        if stops[0] is not None:
            segments.append(('origin_to_stop1', origin_coords, stops[0]))
            segments.append(('stop1_to_destination', stops[0], destination_coords))
    elif num_stops == 2:
        if stops[0] is not None and stops[1] is not None:
            segments.append(('origin_to_stop1', origin_coords, stops[0]))
            segments.append(('stop1_to_stop2', stops[0], stops[1]))
            segments.append(('stop2_to_destination', stops[1], destination_coords))
    
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
            flight.get('stop1_coordinates'),
            flight.get('stop2_coordinates'),
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
    score = np.mean(min_distances)

    return score

def find_best_candidates(flight_data, base_flight_index, num_candidates=10, scoring_method='average'):
    base_flight = flight_data[base_flight_index]
    candidates = []

    for index, candidate_flight in enumerate(flight_data):
        if index != base_flight_index:
            if scoring_method == 'average':
                distance_score = calculate_proximity_score(base_flight, candidate_flight)
                candidates.append((index, distance_score))
    
    # Sort candidates by distance score in ascending order (lower is better) and select the top ones
    candidates.sort(key=lambda x: x[1])  # Lower score is better
    return candidates[:num_candidates]

def finalized_best_candidate(flight_data, base_flight_index, candidate_indices):
    base_flight = flight_data[base_flight_index]
    specialized_candidate_index = None
    best_candidate_score = -float('inf')
    
    base_passengers = base_flight.get('passengers', 0)
    base_net_profit = base_flight.get('net_profit', 0)
    
    for candidate_index in candidate_indices:
        candidate_flight = flight_data[candidate_index]
        candidate_passengers = candidate_flight.get('passengers', 0)
        candidate_net_profit = candidate_flight.get('net_profit', 0)
        candidate_proximity_score = calculate_proximity_score(base_flight, candidate_flight)
        
        # Ensure that the candidate's profit is greater than the base flight's profit
        if candidate_net_profit > base_net_profit and base_passengers + candidate_passengers <= 204:
            combined_score = (candidate_net_profit + candidate_proximity_score)
            
            if combined_score > best_candidate_score:
                best_candidate_score = combined_score
                specialized_candidate_index = candidate_index
    
    return specialized_candidate_index

def path_modified(bad_flight, candidate_flight):
    # Extract and split the stops from both flights, handling None values
    bad_stops = [stop for stop in [bad_flight['origin'], bad_flight.get('stop1', None), bad_flight.get('stop2', None), bad_flight['destination']] if stop is not None]
    candidate_stops = [stop for stop in [candidate_flight['origin'], candidate_flight.get('stop1', None), candidate_flight.get('stop2', None), candidate_flight['destination']] if stop is not None]
    
    # Merge the paths: candidate origin + candidate stops + bad flight stops + candidate destination
    new_path_list = candidate_stops[:1] + candidate_stops[1:-1] + bad_stops[1:-1] + candidate_stops[-1:]
    
    # Remove duplicates while preserving order
    seen = set()
    new_path_filtered = [x for x in new_path_list if not (x in seen or seen.add(x))]

    # Convert the path to a string
    modified_flight_path = ' , '.join(new_path_filtered)
    
    return modified_flight_path

def count_stops(flight_path):
    # Split the flight path into individual airport codes
    airports = flight_path.split(' , ')
    
    # The first and last elements are origin and destination
    origin = airports[0]
    destination = airports[-1]
    
    # Count the number of stops (excluding origin and destination)
    stops = airports[1:-1]
    
    return len(stops), stops

def read_airports_file(file_path):
    airports = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 5:
                try:
                    code, name, population, lon, lat = parts
                    airports[code.strip()] = (float(lon), float(lat))
                except ValueError:
                    continue  # Skip lines with invalid data
    return airports

def reassign_coordinates(modified_flight_path, flight_data, airports_file='airports.txt'):
    # Read airport coordinates from the file
    airports = read_airports_file(airports_file)
    
    # Split the modified flight path into individual airport codes
    path_parts = modified_flight_path.split(' , ')
    
    # Create a list of tuples to store IATA codes and their coordinates
    path_coordinates = []
    
    for code in path_parts:
        if code in airports:
            path_coordinates.append((code, airports[code]))
    
    # Create formatted output for each stop
    formatted_output = []
    for i, (code, coords) in enumerate(path_coordinates):
        formatted_output.append(f"Stop{i+1}: {code}")
        formatted_output.append(f"Stop{i+1} Coordinates: {coords[0]}, {coords[1]}")
    
    # Update the flight data with the new coordinates
    for flight in flight_data:
        if 'origin' in flight and flight['origin'] in path_coordinates:
            flight['origin_coordinates_revised'] = path_coordinates[path_parts.index(flight['origin'])][1]
        
        if 'destination' in flight and flight['destination'] in path_coordinates:
            flight['destination_coordinates_revised'] = path_coordinates[path_parts.index(flight['destination'])][1]
        
        for i in range(6):  # Assuming up to 6 stops
            stop_key = f'stop{i+1}'
            if stop_key in flight and flight[stop_key] in path_coordinates:
                stop_index = path_parts.index(flight[stop_key])
                flight[f'{stop_key}_coordinates_revised'] = path_coordinates[stop_index][1]
    
    return formatted_output

def modified_flight_distances(modified_flight_path, flight_data, formatted_output):
    # Read formatted output to create a dictionary of coordinates
    path_coordinates = {}
    for line in formatted_output:
        if line.startswith("Stop") and "Coordinates" in line:
            parts = line.split(":")
            stop_info = parts[0].strip().split()
            stop_number = int(stop_info[0].replace('Stop', ''))
            coords = parts[1].strip().split(',')
            path_coordinates[stop_number] = (float(coords[0]), float(coords[1]))

    # Include origin (0) and destination (len(formatted_output)//2 + 1)
    path_parts = modified_flight_path.split(' , ')
    num_stops = len(path_parts) - 2  # Exclude origin and destination
    
    # Initialize coordinates list
    coords_list = []
    
    # Extract coordinates for origin
    origin_code = path_parts[0]
    if origin_code in path_coordinates:
        coords_list.append(path_coordinates[0])
    
    # Extract coordinates for each stop
    for i in range(1, num_stops + 1):
        stop_code = path_parts[i]
        if i in path_coordinates:
            coords_list.append(path_coordinates[i])
    
    # Extract coordinates for destination
    destination_code = path_parts[-1]
    if num_stops + 1 in path_coordinates:
        coords_list.append(path_coordinates[num_stops + 1])
    
    # Calculate distances between consecutive points
    total_distance_nm = 0
    for i in range(len(coords_list) - 1):
        total_distance_nm += haversine(coords_list[i], coords_list[i + 1])
    
    return total_distance_nm

def calculate_flight_time(lon1, lat1, lon2, lat2): # Refer back to the generation of flights
    if None in [lat1, lon1, lat2, lon2]:
        return 0, 0  # Handle invalid coordinates
    distance_nm = haversine((lat1, lon1), (lat2, lon2))
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

def update_statistics(flight_data, modified_flight_path, formatted_outputs, finalized_best_candidate):
    # Extract the index of the finalized best candidate
    best_candidate_index = finalized_best_candidate
    
    # Find the finalized best candidate flight data
    finalized_best_flight = flight_data[best_candidate_index]
    
    # Update the flight path
    finalized_best_flight['revised_flight_path_revised'] = modified_flight_path
    
    # Remove the outdated flight (bad flight)
    flight_data = [flight for i, flight in enumerate(flight_data) if i != best_candidate_index]
    
    # Reassign coordinates from formatted_outputs
    path_coordinates = {}
    for line in formatted_outputs:
        if line.startswith("Stop") and "Coordinates" in line:
            parts = line.split(":")
            stop_info = parts[0].strip().split()
            stop_number = int(stop_info[0].replace('Stop', ''))
            coords = parts[1].strip().split(',')
            path_coordinates[stop_number] = (float(coords[0]), float(coords[1]))

    # Extract path parts
    path_parts = modified_flight_path.split(' , ')
    
    # Update flight data with new coordinates
    for flight in flight_data:
        if flight['origin'] in path_coordinates:
            flight['origin_coordinates_revised'] = path_coordinates[0]
        
        if flight['destination'] in path_coordinates:
            flight['destination_coordinates_revised'] = path_coordinates[len(path_coordinates) - 1]
        
        for stop_number in range(1, 7):  # Assuming up to 6 stops
            stop_key = f'stop{stop_number}'
            if stop_key in flight and flight[stop_key] in path_coordinates:
                stop_index = path_parts.index(flight[stop_key])
                flight[f'{stop_key}_coordinates_revised'] = path_coordinates[stop_index]
    
    # Calculate new distances and other statistics
    num_stops, stops = count_stops(modified_flight_path)
    coords_list = []
    for i in range(len(path_parts)):
        code = path_parts[i]
        if i in path_coordinates:
            coords_list.append(path_coordinates[i])
    
    # Calculate total flight distance
    total_distance_nm_revised = 0
    for i in range(len(coords_list) - 1):
        total_distance_nm_revised += haversine(coords_list[i], coords_list[i + 1])
    
    # Calculate flight time and operational cost
    origin_coords = coords_list[0]
    destination_coords = coords_list[-1]
    flight_time_revised, operational_cost_revised = calculate_flight_time(
        origin_coords[1], origin_coords[0],
        destination_coords[1], destination_coords[0]
    )
    
    # Simulate layover and calculate maintenance cost
    layover_time_revised, maintenance_cost_revised = simulate_layover(num_stops, flight_time_revised, operational_cost_revised)
    
    # Calculate flight income
    base_passengers = finalized_best_flight.get('passengers', 0)
    candidate_passengers = flight_data[best_candidate_index].get('passengers', 0)
    combined_passengers_revised = base_passengers + candidate_passengers
    flight_income_revised = 384.85 * combined_passengers_revised
    
    # Calculate net profit
    net_profit_revised = flight_income_revised - operational_cost_revised - maintenance_cost_revised

    # Calculate total passenger miles
    passenger_miles_revised = combined_passengers_revised * total_distance_nm_revised
    
    # Update statistics for the finalized best candidate
    finalized_best_flight.update({
        'distance_nm_revised': total_distance_nm_revised,
        'flight_time_revised': flight_time_revised,
        'operational_cost_revised': operational_cost_revised,
        'maintenance_cost_revised': maintenance_cost_revised,
        'passengers_revised': combined_passengers_revised,
        'flight_income_revised': flight_income_revised,
        'layover_time_revised': layover_time_revised,
        'net_profit_revised': net_profit_revised,
        'total_passenger_miles_revised': passenger_miles_revised,
        'revised': True
    })

    return flight_data

def process_bad_flight(flight_data, bad_flight_index, profit_threshold):
    # Check if the index is valid
    if not (0 <= bad_flight_index < len(flight_data)):
        print(f"Error: Bad flight index {bad_flight_index} is out of range.")
        return flight_data

    # Print the bad flight details
    bad_flight = flight_data[bad_flight_index]
    bad_flight_profit = bad_flight.get('net_profit', 0)
    print(f"\nProcessing Bad Flight {bad_flight_index}:")
    print(f"Profit: ${bad_flight_profit:,.2f}")

    # Print the bad flight route
    bad_flight_route = bad_flight.get('flight_path', [])
    print(f"Bad Flight Route: {bad_flight_route}")

    # If the bad flight's profit is above the threshold, stop the process
    if bad_flight_profit >= profit_threshold:
        print(f"Bad flight {bad_flight_index} has profit above the threshold. No need to process.")
        return flight_data

    # Find the top 10 candidates
    candidates = find_best_candidates(flight_data, bad_flight_index, num_candidates=10)
    
    # Print the top candidates
    print("\nTop Candidates:")
    for index, score in candidates:
        print(f"Candidate Flight {index}: Score {score:.2f}")
    
    # Find the specialized candidate
    candidate_indices = [index for index, score in candidates]
    specialized_candidate_index = finalized_best_candidate(flight_data, bad_flight_index, candidate_indices)
    
    # Print the specialized candidate details
    if specialized_candidate_index is not None:
        specialized_candidate = flight_data[specialized_candidate_index]
        specialized_candidate_profit = specialized_candidate.get('net_profit', 0)
        print(f"\nSpecialized Candidate Flight: {specialized_candidate_index}")
        print(f"Specialized Candidate Profit: ${specialized_candidate_profit:,.2f}")

        # Print the specialized candidate route
        specialized_candidate_route = specialized_candidate.get('flight_path', [])
        print(f"Specialized Candidate Route: {specialized_candidate_route}")

        # Merge the bad flight with the specialized candidate
        print(f"\nMerging Bad Flight {bad_flight_index} with Specialized Candidate Flight {specialized_candidate_index}.")
        
        # Ensure to provide the correct values for `formatted_outputs` and `finalized_best_candidate`
        modified_path = path_modified(bad_flight, specialized_candidate)
        formatted_outputs = reassign_coordinates(modified_path, flight_data)  # Pass flight_data here
        finalized_best_candidate_index = specialized_candidate_index  # Correctly reference the best candidate index
        
        flight_data = update_statistics(flight_data, modified_path, formatted_outputs, finalized_best_candidate_index)
        
        # Print flight paths using path_modified
        print(f"\nModified Flight: {modified_path}")
    else:
        print(f"\nNo suitable specialized candidate found for Bad Flight {bad_flight_index}.")

    return flight_data

def main(scoring_method='average') -> None: # Need help to write new information
    start_time = time.time()
    
    input_file = "sorted_flights.txt"
    output_file = "modified_flights_final.txt"

    # Read input file
    with open(input_file, "r") as file:
        lines = file.readlines()

    flight_data = parse_flight_data_initial(lines)

    # Set the profit threshold to filter flights with profits less than this value
    profit_threshold = 10000  # Change this value to the desired threshold

    # Optimize flights based on the profit threshold
    flight_data = optimize_flights(flight_data, profit_threshold)

    # Write the final optimized flight data to file
    with open(output_file, "w") as file:
        for flight_number, data in enumerate(flight_data):
            file.write(f"Flight: {flight_number}\n")
            file.write(f"Flight Path: {data.get('revised_flight_path_revised', '')}\n")
            file.write(f"Origin: {data.get('origin', '')}\n")
            origin_coords = data.get('origin_coordinates_revised', (0, 0))
            file.write(f"Origin Coordinates: {origin_coords[0]},{origin_coords[1]}\n")
            file.write(f"Destination: {data.get('destination', 'None')}\n")
            destination_coords = data.get('destination_coordinates_revised', (0, 0))
            file.write(f"Destination Coordinates: {destination_coords[0]},{destination_coords[1]}\n")

            for i in range(1, 7):
                stop_key = f'stop{i}'
                stop_coords_key = f'stop{i}_coordinates_revised'
                stop = data.get(stop_key, 'None')
                stop_coords = data.get(stop_coords_key, (0, 0))
                file.write(f"Stop{i}: {stop}\n")
                if stop != 'None':
                    file.write(f"Stop{i} Coordinates: {stop_coords[0]},{stop_coords[1]}\n")
                else:
                    file.write(f"Stop{i} Coordinates: None\n")

            file.write(f"Passengers: {data.get('passengers_revised', 0)}\n")
            file.write(f"Distance (Nautical Miles): {data.get('distance_nm_revised', 0):.2f}\n")
            file.write(f"Flight Time (Hours): {data.get('flight_time_revised', 0):.2f}\n")
            file.write(f"Operating Cost: ${data.get('operational_cost_revised', 0):,.2f}\n")
            file.write(f"Layover Time (Hours): {data.get('layover_time_revised', 0):.2f}\n")
            file.write(f"Maintenance Cost: ${data.get('maintenance_cost_revised', 0):,.2f}\n")
            file.write(f"Income of Flight: ${data.get('flight_income_revised', 0):,.2f}\n")
            file.write(f"Net Profit of the Flight: ${data.get('net_profit_revised', 0):,.2f}\n")
            file.write(f"Total Passenger Miles: {data.get('total_passenger_miles_revised', 0):,.2f} passenger miles.\n")
            file.write("\n")

        if any(flight.get('revised', False) for flight in flight_data):
            file.write("Note: Some flights have been revised.\n")
            file.write("Revised flights are indicated with updated paths and statistics.\n")

    end_time = time.time()
    print(f"\nTotal processing time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
