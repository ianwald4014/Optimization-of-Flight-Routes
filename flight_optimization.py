#!/usr/bin/env python3

import numpy as np
import scipy.integrate as integrate
from math import radians, sin, cos, sqrt, atan2

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

    all_flight_data = []
    for flight_number in flight_data:
        origin = flight_data[flight_number]['origin']
        destination = flight_data[flight_number]['destination']
        stop_cities = []

        if 'stop1' in flight_data[flight_number]:
            stop_cities.append(flight_data[flight_number]['stop1'])
        if 'stop2' in flight_data[flight_number]:
            stop_cities.append(flight_data[flight_number]['stop2'])

        all_flight_data.append((origin, destination, stop_cities, flight_data[flight_number]))
                     
    return all_flight_data

def get_worst_flights_by_profit(flight_data, num_worst=3):
    profits = [(i, flight_info[3]['net_profit']) for i, flight_info in enumerate(flight_data)]
    
    # Sort the flights by profit in ascending order
    profits_sorted = sorted(profits, key=lambda x: x[1])
    
    # Get the worst flights by profit
    worst_flights = profits_sorted[:num_worst]
    
    return worst_flights

# Function to calculate the distance between two coordinates (Haversine formula); will nneed to talk to mentor about this!!
def haversine(coord1, coord2):
    R = 6371  # Radius of the Earth in km
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

# Function to calculate the integral distance between two flight paths
def calculate_integral_distance(path1, path2):
    def integrand(x):
        index = int(x * (len(path1) - 1))
        return haversine(path1[index], path2[index])
    
    total_distance, _ = integrate.quad(integrand, 0, 1)
    return total_distance

# Function to calculate total passenger miles for a flight
def calculate_total_passenger_miles(flight):
    return flight['distance_nm'] * flight['passengers']

def main():
    with open("flights.txt", "r") as file:
        lines = file.readlines()
    
    flight_data = parse_flight_data(lines)
    worst_flights = get_worst_flights_by_profit(flight_data, num_worst=3)
    
    print("Worst flights by profit:")
    for flight in worst_flights:
        flight_index, profit = flight
        print(f"Flight {flight_index}: Profit ${profit}")
        
        path = [
            flight_data[flight_index][3]['origin_coordinates'],
            *([flight_data[flight_index][3]['stop1_coordinates']] if 'stop1_coordinates' in flight_data[flight_index][3] else []),
            *([flight_data[flight_index][3]['stop2_coordinates']] if 'stop2_coordinates' in flight_data[flight_index][3] else []),
            flight_data[flight_index][3]['destination_coordinates']
        ]
        path_str = " -> ".join([
            flight_data[flight_index][3]['origin'],
            *([flight_data[flight_index][3]['stop1']] if 'stop1' in flight_data[flight_index][3] else []),
            *([flight_data[flight_index][3]['stop2']] if 'stop2' in flight_data[flight_index][3] else []),
            flight_data[flight_index][3]['destination']
        ])
        print(f"Route: {path_str}")
    
    # Calculate proximity of all other flights to each of the worst flights
    candidates = {}
    for worst_flight in worst_flights:
        flight_index_worst, _ = worst_flight
        path1 = [
            flight_data[flight_index_worst][3]['origin_coordinates'],
            *([flight_data[flight_index_worst][3]['stop1_coordinates']] if 'stop1_coordinates' in flight_data[flight_index_worst][3] else []),
            *([flight_data[flight_index_worst][3]['stop2_coordinates']] if 'stop2_coordinates' in flight_data[flight_index_worst][3] else []),
            flight_data[flight_index_worst][3]['destination_coordinates']
        ]
        
        distances = []
        for i, flight_info in enumerate(flight_data):
            if i != flight_index_worst:
                path2 = [
                    flight_info[3]['origin_coordinates'],
                    *([flight_info[3]['stop1_coordinates']] if 'stop1_coordinates' in flight_info[3] else []),
                    *([flight_info[3]['stop2_coordinates']] if 'stop2_coordinates' in flight_info[3] else []),
                    flight_info[3]['destination_coordinates']
                ]
                print(f"Comparing Flight {flight_index_worst} to Flight {i}:")
                print(f"Path 1: {path1}")
                print(f"Path 2: {path2}")
                distance = calculate_integral_distance(path1, path2)
                distances.append((i, distance))
        
        # Sort by distance and choose the top 10 closest flights
        candidates[flight_index_worst] = sorted(distances, key=lambda x: x[1])[:10]
    
    # Select the best candidate based on passenger capacity, total passenger miles, and profit
    final_candidates = {}
    for worst_flight in worst_flights:
        flight_index_worst, _ = worst_flight
        worst_flight_info = flight_data[flight_index_worst][3]
        worst_passengers = worst_flight_info['passengers']
        worst_total_passenger_miles = calculate_total_passenger_miles(worst_flight_info)
        
        best_candidate = None
        best_profit = float('-inf')
        
        for candidate in candidates[flight_index_worst]:
            candidate_index, _ = candidate
            candidate_info = flight_data[candidate_index][3]
            candidate_passengers = candidate_info['passengers']
            candidate_total_passenger_miles = calculate_total_passenger_miles(candidate_info)
            candidate_profit = candidate_info['net_profit']
            
            if (candidate_passengers >= worst_passengers and
                candidate_total_passenger_miles > worst_total_passenger_miles and
                candidate_profit > best_profit):
                best_candidate = candidate_index
                best_profit = candidate_profit
        
        if best_candidate is not None:
            final_candidates[flight_index_worst] = best_candidate
    
    # Print the final modified flights
    print("\nFinal modified flights:")
    for worst_index, best_index in final_candidates.items():
        worst_info = flight_data[worst_index][3]
        best_info = flight_data[best_index][3]
        
        modified_flight = { # Need further modifications 
            'origin': worst_info['origin'],
            'destination': best_info['destination'],
            'stops': max(worst_info['stops'], best_info['stops']),
            'passengers': max(worst_info['passengers'], best_info['passengers']),
            'distance_nm': worst_info['distance_nm'] + best_info['distance_nm'],
            'flight_time': worst_info['flight_time'] + best_info['flight_time'],
            'operational_cost': worst_info['operational_cost'] + best_info['operational_cost'],
            'layover_time': worst_info['layover_time'] + best_info['layover_time'],
            'maintenance_cost': worst_info['maintenance_cost'] + best_info['maintenance_cost'],
            'flight_income': worst_info['flight_income'] + best_info['flight_income'],
            'net_profit': worst_info['net_profit'] + best_info['net_profit'],
        }
        
        path_str = " -> ".join([
            modified_flight['origin'],
            *([worst_info['stop1']] if 'stop1' in worst_info else []),
            *([worst_info['stop2']] if 'stop2' in worst_info else []),
            *([best_info['stop1']] if 'stop1' in best_info and 'stop1' not in worst_info else []),
            *([best_info['stop2']] if 'stop2' in best_info and 'stop2' not in worst_info else []),
            modified_flight['destination']
        ])
        
        print(f"Chosen Candidate for Replacement Flight {worst_index}: Flight {best_index}")
        print(f"Flight {worst_index} Route:")
        print(f"Original Flight Path: {flight_data[flight_index][3]['flight_path']}") 
        print(f"Candidate Route: {flight_data[best_index][3]['origin']} -> {flight_data[best_index][3]['destination']}")
        print(f"Modified Flight (Replacing Flight {worst_index}):")
        print(f"Route: {path_str}")
        print(f"Passengers: {modified_flight['passengers']}")
        print(f"Total Distance (NM): {modified_flight['distance_nm']}")
        print(f"Total Flight Time (Hours): {modified_flight['flight_time']}")
        print(f"Total Operational Cost: ${modified_flight['operational_cost']}")
        print(f"Total Layover Time (Hours): {modified_flight['layover_time']}")
        print(f"Total Maintenance Cost: ${modified_flight['maintenance_cost']}")
        print(f"Total Flight Income: ${modified_flight['flight_income']}")
        print(f"Total Net Profit: ${modified_flight['net_profit']}\n")

if __name__ == "__main__":
    main()
