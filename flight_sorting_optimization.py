#!/usr/bin/env python3

import re
from geopy.distance import geodesic
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

    # Extract IATA codes
    origin_iata = data['origin']
    stop1_iata = data.get('stop1', 'None')
    stop2_iata = data.get('stop2', 'None')
    destination_iata = data['destination']

    # Initialize distances based on the number of stops
    distances = {}
    num_stops = data['stops']
    
    # Calculate distances from the origin to each stop and the destination
    if stop1_coords:
        distances['origin_to_stop1'] = haversine(origin_coords, stop1_coords)
    if stop2_coords:
        distances['origin_to_stop2'] = haversine(origin_coords, stop2_coords)
    distances['origin_to_destination'] = haversine(origin_coords, destination_coords)

    # Create a list of tuples (distance, IATA code), only including existing keys
    distances_list = []
    if 'origin_to_stop1' in distances:
        distances_list.append((distances['origin_to_stop1'], stop1_iata))
    if 'origin_to_stop2' in distances:
        distances_list.append((distances['origin_to_stop2'], stop2_iata))
    if 'origin_to_destination' in distances:
        distances_list.append((distances['origin_to_destination'], destination_iata))

    # Sort the list by distance (first element of each tuple)
    distances_list.sort(key=lambda x: x[0])

    return distances_list

def calculate_flight_time(lon1, lat1, lon2, lat2):
    distance_nm = geodesic((lat1, lon1), (lat2, lon2)).nautical
    speed_knots = 485  # Average speed of a Boeing 737 MAX in knots
    flight_time = distance_nm / speed_knots
    operational_cost = 5757 * flight_time
    return flight_time, operational_cost, distance_nm

def reorder_stops(flight_data):
    for flight_number, data in flight_data.items():
        # Store initial coordinates mapping
        iata_to_coords = {}
        if 'origin' in data and 'origin_coordinates' in data:
            iata_to_coords[data['origin']] = data['origin_coordinates']
        if 'stop1' in data and data['stop1'] != 'None' and 'stop1_coordinates' in data:
            iata_to_coords[data['stop1']] = data['stop1_coordinates']
        if 'stop2' in data and data['stop2'] != 'None' and 'stop2_coordinates' in data:
            iata_to_coords[data['stop2']] = data['stop2_coordinates']
        if 'destination' in data and 'destination_coordinates' in data:
            iata_to_coords[data['destination']] = data['destination_coordinates']

        # Get sorted distances
        sorted_distances = calculate_distances(data)

        # Extract sorted IATA codes
        sorted_iatas = [iata for _, iata in sorted_distances if iata != 'None']

        # Reassign coordinates based on sorted IATA codes
        sorted_coords = [iata_to_coords.get(iata, 'None') for iata in sorted_iatas]

        # Update stops and destination
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

        # Update the data with the revised stops and destination
        data['stop1_revised'] = stop1_revised
        data['stop2_revised'] = stop2_revised
        data['destination_revised'] = destination_revised

        # Update the coordinates based on the revised stops
        data['stop1_coordinates'] = iata_to_coords.get(stop1_revised, 'None')
        data['stop2_coordinates'] = iata_to_coords.get(stop2_revised, 'None')
        data['destination_coordinates'] = iata_to_coords.get(destination_revised, 'None')
        
        # Ensure the origin coordinates remain the same
        data['origin_coordinates'] = iata_to_coords.get(data['origin'], 'None')

        # Construct the revised flight path
        data['revised_flight_path'] = f"{data['origin']}, {stop1_revised}, {stop2_revised}, {destination_revised}"

        # Calculate flight time and operational cost for each leg of the trip
        origin_coords = data['origin_coordinates']
        destination_coords = iata_to_coords.get(destination_revised, (None, None))

        # Calculate total distance and other variables
        total_distance_nm = 0
        total_flight_time = 0
        total_operational_cost = 0

        # Calculate for origin to stop1
        if stop1_revised != 'None':
            stop1_coords = iata_to_coords.get(stop1_revised, (None, None))
            if stop1_coords != (None, None):
                flight_time, operational_cost, distance_nm = calculate_flight_time(
                    origin_coords[1], origin_coords[0], stop1_coords[1], stop1_coords[0]
                )
                total_distance_nm += distance_nm
                total_flight_time += flight_time
                total_operational_cost += operational_cost
                origin_coords = stop1_coords  # Move origin to the last stop

        # Calculate for origin/stop1 to stop2
        if stop2_revised != 'None':
            stop2_coords = iata_to_coords.get(stop2_revised, (None, None))
            if stop2_coords != (None, None):
                flight_time, operational_cost, distance_nm = calculate_flight_time(
                    origin_coords[1], origin_coords[0], stop2_coords[1], stop2_coords[0]
                )
                total_distance_nm += distance_nm
                total_flight_time += flight_time
                total_operational_cost += operational_cost
                origin_coords = stop2_coords  # Move origin to the last stop

        # Calculate for the last stop to destination
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

        # Fetch layover time and passengers from the flight data
        layover_time = data['layover_time']
        passengers = data['passengers']

        # Fetch maintenance cost and flight income from the data
        maintenance_cost = data['maintenance_cost']
        flight_income = data['flight_income']

        # Calculate the net profit
        net_profit = flight_income - (maintenance_cost + total_operational_cost)
        data['net_profit'] = net_profit

        # Calculate total passenger miles
        passenger_miles = passengers * total_distance_nm
        data['total_passenger_miles'] = passenger_miles

def write_sorted_flights(flight_data):  # needs to update coordinates
    with open('sorted_flights.txt', 'w') as file:
        file.write("Revising of Flight Routes\n\n")
        for flight_number, data in flight_data.items():
            file.write(f"Flight: {flight_number}\n")
            file.write(f"Flight Path: {data.get('revised_flight_path', '')}\n")
            
            # Write origin and destination
            file.write(f"Origin: {data.get('origin', '')}\n")
            file.write(f"Origin Coordinates: {data['origin_coordinates'][0]},{data['origin_coordinates'][1]}\n")
            file.write(f"Destination: {data.get('destination_revised', 'None')}\n")
            file.write(f"Destination Coordinates: {data['destination_coordinates'][0]},{data['destination_coordinates'][1]}\n")

            # Handle stops
            if data.get('stop1_revised', 'None') != 'None':
                file.write(f"Stop1: {data.get('stop1_revised', 'None')}\n")
                file.write(f"Stop1 Coordinates: {data['stop1_coordinates'][0]},{data['stop1_coordinates'][1]}\n")
            else:
                file.write(f"Stop1: None\n")

            if data.get('stop2_revised', 'None') != 'None':
                file.write(f"Stop2: {data.get('stop2_revised', 'None')}\n")
                file.write(f"Stop2 Coordinates: {data['stop2_coordinates'][0]},{data['stop2_coordinates'][1]}\n")
            else:
                file.write(f"Stop2: None\n")

            # Write remaining data
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
    with open('flights.txt', 'r') as file:
        lines = file.readlines()

    flight_data = parse_flight_data(lines)
    reorder_stops(flight_data)
    write_sorted_flights(flight_data)
    
    print("All flight paths have been sorted successfully within sorted_flights.txt")

if __name__ == "__main__":
    main()
