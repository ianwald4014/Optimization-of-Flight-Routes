#!/usr/bin/env python3

"""Loads a list of flights, calculates the flight path for each, and
writes out a file sorted by total miles flown.  The shortest of those
paths is written out first.
"""

import sys
import pprint
import re
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2

from flight_utils import *

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
        elif line.startswith("Passengers:"):
            flight_data[flight_number]['passengers'] = int(line.split(":")[1].strip())
            current_lines.append(line)
        elif line.startswith("Layover Time (Hours):"):
            flight_data[flight_number]['layover_time'] = float(line.split(":")[1].strip())
            current_lines.append(line)
        elif line.startswith("Maintenance Cost:"):
            flight_data[flight_number]['maintenance_cost'] = float(line.split(": $")[1].strip())
            current_lines.append(line)
        elif line.startswith("Income of Flight:"): 
            flight_data[flight_number]['flight_income'] = float(line.split(": $")[1].strip())
            current_lines.append(line)
        else:
            current_lines.append(line)

    if flight_number is not None:
        flight_data[flight_number]['lines'] = current_lines

    return flight_data

def haversine_distance(coord1, coord2):
    """Calculate the great-circle distance between two points on the Earth's surface."""
    R = 3440.065  # Radius of the Earth in nautical miles
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def calculate_distances(data):
    num_stops = data['stops']
    if num_stops <= 2:
        origin_coords = data['origin_coordinates']
        stop1_coords = data.get('stop1_coordinates', None)
        stop2_coords = data.get('stop2_coordinates', None)
        destination_coords = data['destination_coordinates']

        # Extract IATA codes
        origin_iata = data['origin']
        stop1_iata = data.get('stop1', 'None')
        stop2_iata = data.get('stop2', 'None')
        destination_iata = data['destination']

        # Initialize distances based on the number of stops
        distances = {}
        distances_list = []  # Initialize distances_list here
    
        # Calculate distances from the origin to each stop and the destination
        if stop1_coords:
            distances['origin_to_stop1'] = haversine_distance(origin_coords, stop1_coords)
        if stop2_coords:
            distances['origin_to_stop2'] = haversine_distance(origin_coords, stop2_coords)
        distances['origin_to_destination'] = haversine_distance(origin_coords, destination_coords)

        # Create a list of tuples (distance, IATA code), only including existing keys
        if 'origin_to_stop1' in distances:
            distances_list.append((distances['origin_to_stop1'], stop1_iata))
        if 'origin_to_stop2' in distances:
            distances_list.append((distances['origin_to_stop2'], stop2_iata))
        if 'origin_to_destination' in distances:
            distances_list.append((distances['origin_to_destination'], destination_iata))

        # Sort the list by distance (first element of each tuple)
        distances_list.sort(key=lambda x: x[0])
        
        return distances_list

def calculate_additional_distances(data):
    num_stops = data['stops']
    if num_stops > 2:
        origin_coords = data['origin_coordinates']
        destination_coords = data['destination_coordinates']
        
        # Extract IATA codes
        origin_iata = data['origin']
        destination_iata = data['destination']
        
        # Initialize distances and stops list
        distances = []
        
        # Calculate distances from the origin to each stop and the destination
        for i in range(1, num_stops + 1):
            stop_coords = data.get(f'stop{i}_coordinates', None)
            stop_iata = data.get(f'stop{i}', 'None')
            if stop_coords:
                distance = haversine_distance(origin_coords, stop_coords)
                distances.append((distance, stop_iata))
        
        # Add distance to the destination
        distance_to_destination = haversine_distance(origin_coords, destination_coords)
        distances.append((distance_to_destination, destination_iata))

        # Sort the list by distance (first element of each tuple)
        distances.sort(key=lambda x: x[0])
        
        return distances
    else:
        return []

def calculate_flight_time(lon1, lat1, lon2, lat2):
    """Calculate flight time and operational cost."""
    if None in [lat1, lon1, lat2, lon2]:
        return 0, 0, 0  # Handle invalid coordinates
    distance_nm = haversine_distance((lat1, lon1), (lat2, lon2))
    speed_knots = 485  # Average speed of a Boeing 737 MAX in knots
    flight_time = distance_nm / speed_knots
    operational_cost = 5757 * flight_time
    return flight_time, operational_cost, distance_nm

def simulate_layover(stops, flight_time, operational_cost):
    """Simulate layover time and calculate maintenance cost."""
    layover_time = 0
    maintenance_cost = 0
    
    if stops > 0:
        layover_time = 1.5 * stops  # Layover time in hours
        maintenance_cost_per_hour = 150  # Maintenance cost per hour
        maintenance_cost = (layover_time * maintenance_cost_per_hour) + operational_cost
    else:
        maintenance_cost = operational_cost

    return layover_time, maintenance_cost

def reorder_stops(flight_data):
    for flight_number, data in flight_data.items():
        num_stops = data['stops']
        if num_stops <= 2:
            sorted_distances = calculate_distances(data)
        else:
            sorted_distances = calculate_additional_distances(data)

        # Store initial coordinates mapping
        iata_to_coords = {}
        for iata_key in ['origin', 'destination'] + [f'stop{i}' for i in range(1, num_stops + 1)]:
            coords_key = f"{iata_key}_coordinates"
            if iata_key in data and coords_key in data:
                iata_to_coords[data[iata_key]] = data[coords_key]

        # Extract sorted IATA codes
        sorted_iatas = [iata for _, iata in sorted_distances if iata != 'None']

        # Reassign coordinates based on sorted IATA codes
        sorted_coords = [iata_to_coords.get(iata, (None, None)) for iata in sorted_iatas]

        # Update stops and destination based on the sorted IATA codes
        for i in range(1, num_stops + 1):
            if i <= len(sorted_iatas):
                data[f'stop{i}_revised'] = sorted_iatas[i - 1]
                data[f'stop{i}_coordinates'] = sorted_coords[i - 1]
            else:
                data[f'stop{i}_revised'] = 'None'
                data[f'stop{i}_coordinates'] = (None, None)

        # Update the destination
        if len(sorted_iatas) >= num_stops:
            data['destination_revised'] = sorted_iatas[num_stops]
            data['destination_coordinates'] = sorted_coords[num_stops]
        else:
            data['destination_revised'] = 'None'
            data['destination_coordinates'] = (None, None)

        # Ensure the origin coordinates remain the same
        data['origin_coordinates'] = iata_to_coords.get(data['origin'], (None, None))

        # Construct the revised flight path
        stops_revised = ', '.join([data[f'stop{i}_revised'] for i in range(1, num_stops + 1) if data[f'stop{i}_revised'] != 'None'])
        data['revised_flight_path'] = f"{data['origin']}, {stops_revised}, {data['destination_revised']}"

        # Calculate flight time and operational cost for each leg of the trip
        origin_coords = data['origin_coordinates']
        destination_coords = iata_to_coords.get(data['destination_revised'], (None, None))

        total_distance_nm = 0
        total_flight_time = 0
        total_operational_cost = 0

        for i in range(1, num_stops + 1):
            stop_revised = data[f'stop{i}_revised']
            if stop_revised != 'None':
                stop_coords = iata_to_coords.get(stop_revised, (None, None))
                if stop_coords != (None, None):
                    flight_time, operational_cost, distance_nm = calculate_flight_time(
                        origin_coords[1], origin_coords[0], stop_coords[1], stop_coords[0]
                    )
                    total_distance_nm += distance_nm
                    total_flight_time += flight_time
                    total_operational_cost += operational_cost
                    origin_coords = stop_coords

        if destination_coords != (None, None):
            flight_time, operational_cost, distance_nm = calculate_flight_time(
                origin_coords[1], origin_coords[0], destination_coords[1], destination_coords[0]
            )
            total_distance_nm += distance_nm
            total_flight_time += flight_time
            total_operational_cost += operational_cost

        data['flight_time'] = total_flight_time
        data['operating_cost'] = total_operational_cost
        data['distance_nm'] = total_distance_nm

        # Fetch passengers from the flight data          
        passengers = data['passengers']

        # Recalculate layover time and maintenance cost
        layover_time, maintenance_cost = simulate_layover(num_stops, total_flight_time, total_operational_cost)
        data['layover_time'] = layover_time
        data['maintenance_cost'] = maintenance_cost
        
        # Fetch flight income from the data
        flight_income = data['flight_income']

        # Calculate the net profit
        net_profit = flight_income - maintenance_cost
        data['net_profit'] = net_profit

        # Calculate total passenger miles
        passenger_miles = passengers * total_distance_nm
        data['total_passenger_miles'] = passenger_miles

    return flight_data

def write_sorted_flights(flight_data):
    pprint.pprint(flight_data)
    return                      # FIXME:

    file_name = 'sorted_flights.txt'  # Change this to 'modified_flights_final.txt' if needed
    with open(file_name, 'w') as file:
        file.write("Revising of Flight Routes\n\n")
        for flight_number, data in flight_data.items():
            num_stops = data['stops']
            file.write(f"Flight: {flight_number}\n")
            
            # Properly format the flight path based on the number of stops
            if num_stops == 0:
                flight_path = f"{data.get('origin', '')}, {data.get('destination_revised', 'None')}"
            else:
                stops_revised = [data.get(f'stop{i}_revised', 'None') for i in range(1, num_stops + 1)]
                flight_path = f"{data.get('origin', '')}, {', '.join(stops_revised)}, {data.get('destination_revised', 'None')}"
            
            file.write(f"Flight Path: {flight_path}\n")
            file.write(f"Origin: {data.get('origin', '')}\n")
            file.write(f"Origin Coordinates: {data['origin_coordinates'][0]},{data['origin_coordinates'][1]}\n")
            file.write(f"Destination: {data.get('destination_revised', 'None')}\n")
            file.write(f"Destination Coordinates: {data['destination_coordinates'][0]},{data['destination_coordinates'][1]}\n")
            file.write(f"Stops: {data['stops']}\n")
            
            # Only print stop information if stops are present
            for i in range(1, num_stops + 1):
                stop_revised = data.get(f'stop{i}_revised', 'None')
                if stop_revised != 'None':
                    file.write(f"Stop{i}: {stop_revised}\n")
                    file.write(f"Stop{i} Coordinates: {data[f'stop{i}_coordinates'][0]},{data[f'stop{i}_coordinates'][1]}\n")
            
            file.write(f"Passengers: {data.get('passengers', 0)}\n")
            file.write(f"Distance (Nautical Miles): {data.get('distance_nm', 0):.2f}\n")
            file.write(f"Flight Time (Hours): {data.get('flight_time', 0):.2f}\n")
            file.write(f"Operating Cost: ${data.get('operating_cost', 0):.2f}\n")
            file.write(f"Layover Time (Hours): {data.get('layover_time', 0):.2f}\n")
            file.write(f"Maintenance Cost: ${data.get('maintenance_cost', 0):.2f}\n")
            file.write(f"Income of Flight: ${data.get('flight_income', 0):.2f}\n")
            file.write(f"Net Profit of the Flight: ${data.get('net_profit', 0):.2f}\n")
            file.write(f"Total Passenger Miles: {data.get('total_passenger_miles', 0):.2f} passenger miles.\n")
            file.write("\n")

def main():
    file_name = 'flights.txt'   # Change this to 'modified_flights_final.txt' if needed
    file_name_newstyle = 'generated_flights_new.txt'
    if len(sys.argv) > 2:
        raise Exception('Too many arguments')
    elif len(sys.argv) == 2:
        file_name_newstyle = sys.argv[1]

    # oldstyle approach
    with open('flights.txt', 'r') as file:
        lines = file.readlines()

    flight_data = parse_flight_data(lines)
    reorder_stops(flight_data)
    write_sorted_flights(flight_data)

    # then do the newstyle approach
    all_flights_new = load_flights_newstyle(file_name_newstyle)
    print('============ what I just loaded ================')
    pprint.pprint(all_flights_new)
    print('================== (DONE) ======================')
    ordered_flights = reorder_stops_new(all_flights_new)
    write_flights_newstyle('sorted_flights_new.txt', ordered_flights)

def reorder_stops_new(all_flights):
    """Takes a list of all the flight routes and reorders *each* flight
    path by its total distance traveled."""
    reordered_flight_list = []
    for record in all_flights:
        orig_city_order = flight_path2city_list(record['flight_path'])
        orig_distance = calc_distance_new(orig_city_order)
        new_city_order = rearrange_cities_for_shortest_path(orig_city_order)
        new_distance = calc_distance_new(new_city_order)
        print('REORDER:', record['flight_number'], orig_distance, new_city_order, new_distance)
        new_record = record
        new_record['flight_path'] = ', '.join(new_city_order)
        reordered_flight_list.append(new_record)
    return reordered_flight_list

        
if __name__ == "__main__":
    main()
