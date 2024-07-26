import numpy as np
import scipy.integrate as integrate
from math import radians, sin, cos, sqrt, atan2

# Function to parse the flight data from the file
def parse_flight_data(lines):
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
        elif line.startswith("Total Passenger Miles:"):
            continue

    return list(flight_data.values())

# Get the worst flights by profit
def get_worst_flights_by_profit(flight_data, num_worst=3):
    profits = [(i, flight_info['net_profit']) for i, flight_info in enumerate(flight_data)]
    sorted_profits = sorted(profits, key=lambda x: x[1])
    return sorted_profits[:num_worst]

# Haversine formula to compute distance between two coordinates
def haversine(coord1, coord2):
    R = 3440.065  # Radius of the Earth in nautical miles
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def calculate_distances(data):
    origin_coords = data['origin_coordinates']
    stop1_coords = data.get('stop1_coordinates', None)
    stop2_coords = data.get('stop2_coordinates', None)
    destination_coords = data['destination_coordinates']
    
    distances = {}
    num_stops = data['stops']
    
    # Calculate distances based on available coordinates
    if stop1_coords is not None:
        distances['origin_to_stop1'] = haversine(origin_coords, stop1_coords)
    
    if stop1_coords is not None and stop2_coords is not None:
        distances['stop1_to_stop2'] = haversine(stop1_coords, stop2_coords)
    
    if stop2_coords is not None and destination_coords is not None:
        distances['stop2_to_destination'] = haversine(stop2_coords, destination_coords)
    
    if stop1_coords is None and stop2_coords is None:
        distances['origin_to_destination'] = haversine(origin_coords, destination_coords)
    
    # Calculate the total distance based on the number of stops
    if num_stops == 0:
        if 'origin_to_destination' in distances:
            distance_of_route = distances['origin_to_destination']
        else:
            raise ValueError("Insufficient data to calculate distance with 0 stops.")
    elif num_stops == 1:
        if 'origin_to_stop1' in distances and 'stop1_to_destination' in distances:
            distance_of_route = (distances['origin_to_stop1'] +
                                 distances['stop1_to_destination'])
        else:
            raise ValueError("Insufficient data to calculate distance with 1 stop.")
    elif num_stops == 2:
        if ('origin_to_stop1' in distances and 
            'stop1_to_stop2' in distances and 
            'stop2_to_destination' in distances):
            distance_of_route = (distances['origin_to_stop1'] +
                                 distances['stop1_to_stop2'] +
                                 distances['stop2_to_destination'])
        else:
            raise ValueError("Insufficient data to calculate distance with 2 stops.")
    else:
        raise ValueError("Invalid number of stops. Only 0, 1, or 2 stops are supported.")
    
    return distance_of_route

# Calculate the integral distance
def calculate_distances(data):
    origin_coords = data['origin_coordinates']
    stop1_coords = data.get('stop1_coordinates', None)
    stop2_coords = data.get('stop2_coordinates', None)
    destination_coords = data['destination_coordinates']
    
    distances = {}
    num_stops = data['stops']
    
    # Calculate distances based on available coordinates
    if stop1_coords is not None:
        distances['origin_to_stop1'] = haversine(origin_coords, stop1_coords)
    
    if stop1_coords is not None and stop2_coords is not None:
        distances['stop1_to_stop2'] = haversine(stop1_coords, stop2_coords)
    
    if stop2_coords is not None and destination_coords is not None:
        distances['stop2_to_destination'] = haversine(stop2_coords, destination_coords)
    
    if stop1_coords is None and stop2_coords is None:
        distances['origin_to_destination'] = haversine(origin_coords, destination_coords)
    
    # Calculate the total distance based on the number of stops
    if num_stops == 0:
        if 'origin_to_destination' in distances:
            distance_of_route = distances['origin_to_destination']
        else:
            raise ValueError("Insufficient data to calculate distance with 0 stops.")
    elif num_stops == 1:
        if 'origin_to_stop1' in distances and 'stop1_to_destination' in distances:
            distance_of_route = (distances['origin_to_stop1'] +
                                 distances['stop1_to_destination'])
        else:
            raise ValueError("Insufficient data to calculate distance with 1 stop.")
    elif num_stops == 2:
        if ('origin_to_stop1' in distances and 
            'stop1_to_stop2' in distances and 
            'stop2_to_destination' in distances):
            distance_of_route = (distances['origin_to_stop1'] +
                                 distances['stop1_to_stop2'] +
                                 distances['stop2_to_destination'])
        else:
            raise ValueError("Insufficient data to calculate distance with 2 stops.")
    else:
        raise ValueError("Invalid number of stops. Only 0, 1, or 2 stops are supported.")
    
    return distance_of_route

# Calculating the proximity of the bad and candidate flight paths
def calculate_sum_distance_score(path1, path2):
    """
    Calculates the sum of all smallest distances between segments of path1 and path2.
    """
    def segment_distance(p1, p2):
        return haversine(p1, p2)

    def calculate_distances_between_segments(path):
        distances = []
        for i in range(len(path) - 1):
            distances.append(segment_distance(path[i], path[i + 1]))
        return distances

    distances1 = calculate_distances_between_segments(path1)
    distances2 = calculate_distances_between_segments(path2)

    # Make sure both lists have the same length
    length = min(len(distances1), len(distances2))
    distances1 = sorted(distances1)[:length]
    distances2 = sorted(distances2)[:length]

    # Sum of smallest distances
    return sum(min(d1, d2) for d1, d2 in zip(distances1, distances2))

def calculate_smallest_distance_score(path1, path2):
    """
    Calculates the smallest distance between any (x, y) coordinate pairs of path1 and path2.
    """
    def extract_coordinates(path):
        coords = []
        for i in range(len(path)):
            coords.append(path[i])
        return coords

    coords1 = extract_coordinates(path1)
    coords2 = extract_coordinates(path2)

    min_distance = float('inf')

    for coord1 in coords1:
        for coord2 in coords2:
            distance = haversine(coord1, coord2)
            if distance < min_distance:
                min_distance = distance

    return min_distance

# Find best flight candidates for merging based on caclulated distances
def find_best_candidates(flight_data, base_flight_index, num_candidates=10, scoring_method='sum'):
    base_flight = flight_data[base_flight_index]
    base_path = [
        base_flight['origin_coordinates'],
        *([base_flight['stop1_coordinates']] if 'stop1_coordinates' in base_flight else []),
        *([base_flight['stop2_coordinates']] if 'stop2_coordinates' in base_flight else []),
        base_flight['destination_coordinates']
    ]
    
    candidates = []
    for index, flight in enumerate(flight_data):
        if index == base_flight_index:
            continue
        
        path = [
            flight['origin_coordinates'],
            *([flight['stop1_coordinates']] if 'stop1_coordinates' in flight else []),
            *([flight['stop2_coordinates']] if 'stop2_coordinates' in flight else []),
            flight['destination_coordinates']
        ]
        
        # Use the appropriate scoring method
        if scoring_method == 'sum':
            distance_score = calculate_sum_distance_score(base_path, path)
        elif scoring_method == 'smallest':
            distance_score = calculate_smallest_distance_score(base_path, path)
        else:
            raise ValueError("Invalid scoring method. Choose 'sum' or 'smallest'.")
        
        candidates.append((index, distance_score))
    
    sorted_candidates = sorted(candidates, key=lambda x: x[1])
    return sorted_candidates[:num_candidates]

# Find best flight candidates for merging based on integral distance
def find_best_candidates(flight_data, base_flight_index, num_candidates=10, scoring_method='sum'):
    base_flight = flight_data[base_flight_index]
    base_path = [
        base_flight['origin_coordinates'],
        *([base_flight['stop1_coordinates']] if 'stop1_coordinates' in base_flight else []),
        *([base_flight['stop2_coordinates']] if 'stop2_coordinates' in base_flight else []),
        base_flight['destination_coordinates']
    ]
    
    candidates = []
    for index, flight in enumerate(flight_data):
        if index == base_flight_index:
            continue
        
        path = [
            flight['origin_coordinates'],
            *([flight['stop1_coordinates']] if 'stop1_coordinates' in flight else []),
            *([flight['stop2_coordinates']] if 'stop2_coordinates' in flight else []),
            flight['destination_coordinates']
        ]
        
        # Use the appropriate scoring method
        if scoring_method == 'sum':
            distance_score = calculate_sum_distance_score(base_path, path)
        elif scoring_method == 'smallest':
            distance_score = calculate_smallest_distance_score(base_path, path)
        else:
            raise ValueError("Invalid scoring method. Choose 'sum' or 'smallest'.")
        
        candidates.append((index, distance_score))
    
    sorted_candidates = sorted(candidates, key=lambda x: x[1])
    return sorted_candidates[:num_candidates]

# def best_candidate_stops(flight_data): 

# Calculate total passenger miles
def calculate_total_passenger_miles(flight):
    return flight['distance_nm'] * flight['passengers']

# Main function to execute the script
def main(run, scoring_method='sum'):
    # Determine input and output filenames based on the run number
    input_file = f"sorted_flights.txt" if run == 0 else f"modified_flights_{run - 1}.txt"
    output_file = f"modified_flights_{run}.txt"

    # Read the flight data from the appropriate file
    with open(input_file, "r") as file:
        lines = file.readlines()

    flight_data = parse_flight_data(lines)

    # Ensure each flight dictionary has a unique identifier for easier access
    for i, flight in enumerate(flight_data):
        flight['flight_number'] = i  # Assuming index can be used as flight_number

    worst_flights = get_worst_flights_by_profit(flight_data, num_worst=3)
    
    print("Worst flights by profit:")
    best_candidates = {}  # To store the best candidate for each bad flight

    for flight in worst_flights:
        flight_index, profit = flight
        print(f"Flight {flight_index}: Profit ${profit:.2f}")

        path_str = ", ".join([
            flight_data[flight_index]['origin'],
            *([flight_data[flight_index].get(f'stop{i+1}', '') for i in range(flight_data[flight_index]['stops'])]),
            flight_data[flight_index]['destination']
        ])
        print(f"Flight Path: {path_str}")

        candidates = find_best_candidates(flight_data, flight_index, scoring_method=scoring_method)

        print(f"\nPotentially optimal flights for merging with Flight {flight_index}:")
        for candidate_index, distance in candidates:
            print(f"Candidate Flight {candidate_index}: Distance {distance:.2f} NM")

        # Find the best candidate that can accommodate all passengers and has higher net profit
        best_candidate = None
        for candidate_index, _ in candidates:
            candidate = flight_data[candidate_index]
            if candidate['net_profit'] > flight_data[flight_index]['net_profit'] and \
               candidate['passengers'] >= flight_data[flight_index]['passengers'] + flight_data[flight_index]['passengers']:
                best_candidate = candidate_index
                break

        if best_candidate is not None:
            print(f"\nBest candidate for merging with Flight {flight_index} is Flight {best_candidate}")
            # Update the flight path of the bad flight to include stops from the best candidate
            candidate_flight = flight_data[best_candidate]
            updated_path = [
                candidate_flight['origin'],
                *([flight_data[flight_index].get(f'stop{i+1}', '') for i in range(flight_data[flight_index]['stops'])]),
                candidate_flight['destination']
            ]
            flight_data[flight_index]['flight_path'] = ", ".join(updated_path)
            print(f"Updated Flight Path for Flight {flight_index}: {flight_data[flight_index]['flight_path']}")
            
            # Store the best candidate index to be removed later
            best_candidates[best_candidate] = flight_data[best_candidate]

    total_passenger_miles = sum(calculate_total_passenger_miles(flight) for flight in flight_data)
    print(f"\nTotal Passenger Miles for the airline: {total_passenger_miles:.2f} NM")

    with open(output_file, "w") as file:
        for flight in flight_data:
            if flight['flight_number'] not in best_candidates:
                # Ensure all required keys are present before writing
                file.write(f"Flight: {flight.get('flight_number', 'N/A')}\n")
                file.write(f"Flight Path: {flight.get('flight_path', 'N/A')}\n")
                file.write(f"Origin: {flight.get('origin', 'N/A')}\n")
                origin_coords = flight.get('origin_coordinates', (0, 0))
                file.write(f"Origin Coordinates: {origin_coords[0]}, {origin_coords[1]}\n")
                file.write(f"Destination: {flight.get('destination', 'N/A')}\n")
                dest_coords = flight.get('destination_coordinates', (0, 0))
                file.write(f"Destination Coordinates: {dest_coords[0]}, {dest_coords[1]}\n")
                file.write(f"Stops: {flight.get('stops', 0)}\n")
                for i in range(6):  # Adjust if the number of stops changes
                    stop_key = f'stop{i+1}'
                    if stop_key in flight:
                        file.write(f"{stop_key.capitalize()}: {flight.get(stop_key, 'N/A')}\n")
                        stop_coords_key = f'stop{i+1}_coordinates'
                        stop_coords = flight.get(stop_coords_key, (0, 0))
                        file.write(f"{stop_coords_key.replace('_coordinates', ' Coordinates')}: {stop_coords[0]}, {stop_coords[1]}\n")
                file.write(f"Passengers: {flight.get('passengers', 0)}\n")
                file.write(f"Distance (Nautical Miles): {flight.get('distance_nm', 0)}\n")
                file.write(f"Flight Time (Hours): {flight.get('flight_time', 0)}\n")
                file.write(f"Operating Cost: ${flight.get('operational_cost', 0)}\n")
                file.write(f"Layover Time (Hours): {flight.get('layover_time', 0)}\n")
                file.write(f"Maintenance Cost: ${flight.get('maintenance_cost', 0)}\n")
                file.write(f"Income of Flight: ${flight.get('flight_income', 0)}\n")
                file.write(f"Net Profit of the Flight: ${flight.get('net_profit', 0)}\n")
                file.write("\n")

if __name__ == "__main__":
    # Number of runs can be set here
    num_runs = 5  # Adjust as needed
    for run in range(num_runs):
        main(run, scoring_method='sum')  # Change 'sum' to 'smallest' for the smallest distance scoring
