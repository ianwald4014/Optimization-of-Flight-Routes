#!/usr/bin/env python3

import re
from math import radians, sin, cos, sqrt, atan2

def parse_flight_data(lines):
    flight_data = {}
    flight_number = None
    current_lines = []

    for line in lines:
        if line.startswith("Flight:"):
            if flight_number is not None:
                flight_data[flight_number]['lines'] = current_lines
            flight_number = int(line.split(":")[1].strip())
            flight_data[flight_number] = {}
            current_lines = [line]
        elif line.startswith("Flight Path:"):
            flight_data[flight_number]['flight_path'] = line.split(":")[1].strip()
            current_lines.append(line)
        elif line.startswith("Origin:"):
            flight_data[flight_number]['origin'] = line.split(":")[1].strip().split()[0]
            current_lines.append(line)
        elif line.startswith("Origin Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['origin_coordinates'] = (float(coords[0]), float(coords[1]))
            current_lines.append(line)
        elif line.startswith("Destination:"):
            flight_data[flight_number]['destination'] = line.split(":")[1].strip().split()[0]
            current_lines.append(line)
        elif line.startswith("Destination Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['destination_coordinates'] = (float(coords[0]), float(coords[1]))
            current_lines.append(line)
        elif line.startswith("Stops:"):
            flight_data[flight_number]['stops'] = int(line.split(":")[1].strip())
            current_lines.append(line)
        elif line.startswith("Stop1:"):
            stop1 = line.split(":")[1].strip().split()[0]
            if stop1 != "None":
                flight_data[flight_number]['stop1'] = stop1
            current_lines.append(line)
        elif line.startswith("Stop1 Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['stop1_coordinates'] = (float(coords[0]), float(coords[1]))
            current_lines.append(line)
        elif line.startswith("Stop2:"):
            stop2 = line.split(":")[1].strip().split()[0]
            if stop2 != "None":
                flight_data[flight_number]['stop2'] = stop2
            current_lines.append(line)
        elif line.startswith("Stop2 Coordinates:"):
            coords = line.split(":")[1].strip().split(",")
            flight_data[flight_number]['stop2_coordinates'] = (float(coords[0]), float(coords[1]))
            current_lines.append(line)
        else:
            current_lines.append(line)

    if flight_number is not None:
        flight_data[flight_number]['lines'] = current_lines

    return flight_data

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
    stop1_coords = data.get('stop1_coordinates', origin_coords)
    stop2_coords = data.get('stop2_coordinates', origin_coords)
    destination_coords = data['destination_coordinates']

    # Extract IATA codes
    stop1_iata = data.get('stop1', 'None')
    stop2_iata = data.get('stop2', 'None')
    destination_iata = data['destination']

    # Initialize distances dictionary based on the number of stops
    distances = {}
    num_stops = data['stops']
    
    if num_stops == 0:
        distances['from_origin_to_destination'] = haversine(origin_coords, destination_coords)
    elif num_stops == 1:
        if stop1_iata != 'None':
            distances['from_origin_to_stop1'] = haversine(origin_coords, stop1_coords)
            distances['from_origin_to_destination'] = haversine(stop1_coords, destination_coords)
    elif num_stops == 2:
        if stop1_iata != 'None':
            distances['from_origin_to_stop1'] = haversine(origin_coords, stop1_coords)
        if stop2_iata != 'None':
            distances['from_origin_to_stop2'] = haversine(stop1_coords, stop2_coords)
        distances['from_origin_to_destination'] = haversine(stop2_coords, destination_coords)

    # Create a list of tuples (distance, IATA code), only including existing keys
    distances_list = []
    if 'from_origin_to_stop1' in distances:
        distances_list.append((distances['from_origin_to_stop1'], stop1_iata))
    if 'from_origin_to_stop2' in distances:
        distances_list.append((distances['from_origin_to_stop2'], stop2_iata))
    if 'from_origin_to_destination' in distances:
        distances_list.append((distances['from_origin_to_destination'], destination_iata))

    # Sort the list by distance (first element of each tuple)
    distances_list.sort(key=lambda x: x[0])

    return distances_list

def reorder_stops(flight_data):
    for flight_number, data in flight_data.items():
        # Get sorted distances
        sorted_distances = calculate_distances(data)

        # Extract sorted labels
        sorted_iatas = [iata for _, iata in sorted_distances if iata != 'None']

        # Handle different cases based on the number of stops
        if len(sorted_iatas) == 1:
            stop1_revised = 'None'
            stop2_revised = 'None'
            destination_revised = sorted_iatas[0]
        elif len(sorted_iatas) == 2:
            stop1_revised = sorted_iatas[0]
            stop2_revised = 'None'
            destination_revised = sorted_iatas[1]
        else:
            stop1_revised = sorted_iatas[0]
            stop2_revised = sorted_iatas[1]
            destination_revised = sorted_iatas[2]

        # Update the data dictionary with the revised stops and destination
        data['stop1_revised'] = stop1_revised
        data['stop2_revised'] = stop2_revised
        data['destination_revised'] = destination_revised

        # Construct the revised flight path
        data['revised_flight_path'] = f"{data['origin']}, {stop1_revised}, {stop2_revised}, {destination_revised}"

def write_sorted_flights(flight_data):
    with open('sorted_flights.txt', 'w') as file:
        file.write("Revising of Flight Routes\n\n")
        for flight_number, data in flight_data.items():
            for line in data.get('lines', []):
                if line.startswith("Flight Path:"):
                    file.write(f"Flight Path: {data.get('revised_flight_path', '')}\n")
                elif line.startswith("Stop1:"):
                    file.write(f"Stop1: {data.get('stop1_revised', 'None')}\n")
                elif line.startswith("Stop2:"):
                    file.write(f"Stop2: {data.get('stop2_revised', 'None')}\n")
                elif line.startswith("Destination:"):
                    file.write(f"Destination: {data.get('destination_revised', 'None')}\n")
                else:
                    file.write(line)

def main():
    with open('flights.txt', 'r') as file:
        lines = file.readlines()

    flight_data = parse_flight_data(lines)
    reorder_stops(flight_data)
    write_sorted_flights(flight_data)
    
    print("All flight paths have been sorted successfully within sorted_flights.txt")

if __name__ == "__main__":
    main()
