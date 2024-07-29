#! /usr/bin/env python3

import random
from math import radians, sin, cos, sqrt, atan2

# Airport data with latitude and longitude
airports = {
    'LAX': {'lat': 34.0522, 'lon': -118.2437},
    'PHX': {'lat': 33.4484, 'lon': -112.074},
    'DEN': {'lat': 39.7392, 'lon': -104.9903},
    'DFW': {'lat': 32.8975, 'lon': -97.0404},
    'JFK': {'lat': 40.6413, 'lon': -73.7781},
    'MIA': {'lat': 25.7617, 'lon': -80.1918},
    'SEA': {'lat': 47.6062, 'lon': -122.3321},
    'ORD': {'lat': 41.9786, 'lon': -87.9048},
    'ABQ': {'lat': 35.0844, 'lon': -106.6504},
    'MCI': {'lat': 39.2978, 'lon': -94.7139},
}

def haversine_distance_nm(lat1, lon1, lat2, lon2):
    """Calculate distance in nautical miles using the haversine formula."""
    R = 3440.065  # Radius of Earth in nautical miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance_nm = R * c
    return distance_nm

def calculate_flight_time(lon1, lat1, lon2, lat2):
    """Calculate flight time and operational cost."""
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

# Initialize variables
routes = []
route_id = 1
total_passenger_miles = 0

# Generate all possible routes
for origin_code, origin_data in airports.items():
    for dest_code, dest_data in airports.items():
        if origin_code != dest_code:  # Ensure origin and destination are different

            # Initialize distance and time
            total_distance_nm = 0
            total_flight_time = 0
            total_operating_cost = 0

            # Determine number of stops based on distance
            distance_nm = haversine_distance_nm(origin_data['lat'], origin_data['lon'], dest_data['lat'], dest_data['lon'])
            if distance_nm > 434.488:  # 500 miles in nautical miles
                possible_stops = [code for code in airports.keys() if code not in [origin_code, dest_code]]
                stops = random.randint(0, min(2, len(possible_stops)))
                stop_cities = random.sample(possible_stops, stops)
                
                stop1 = stop_cities[0] if stops >= 1 else 'None'
                stop2 = stop_cities[1] if stops >= 2 else 'None'
                
                stop1_data = airports.get(stop1, {'lat': None, 'lon': None})
                stop2_data = airports.get(stop2, {'lat': None, 'lon': None})

                if stop1 != 'None' and None not in [stop1_data['lat'], stop1_data['lon']]:
                    # Calculate distance and time for origin to stop1
                    distance_leg1 = haversine_distance_nm(origin_data['lat'], origin_data['lon'], stop1_data['lat'], stop1_data['lon'])
                    flight_time_leg1, operating_cost_leg1 = calculate_flight_time(origin_data['lon'], origin_data['lat'], stop1_data['lon'], stop1_data['lat'])
                    total_distance_nm += distance_leg1
                    total_flight_time += flight_time_leg1
                    total_operating_cost += operating_cost_leg1

                    if stop2 != 'None' and None not in [stop2_data['lat'], stop2_data['lon']]:
                        # Calculate distance and time for stop1 to stop2
                        distance_leg2 = haversine_distance_nm(stop1_data['lat'], stop1_data['lon'], stop2_data['lat'], stop2_data['lon'])
                        flight_time_leg2, operating_cost_leg2 = calculate_flight_time(stop1_data['lon'], stop1_data['lat'], stop2_data['lon'], stop2_data['lat'])
                        total_distance_nm += distance_leg2
                        total_flight_time += flight_time_leg2
                        total_operating_cost += operating_cost_leg2

                        # Calculate distance and time for stop2 to destination
                        distance_leg3 = haversine_distance_nm(stop2_data['lat'], stop2_data['lon'], dest_data['lat'], dest_data['lon'])
                        flight_time_leg3, operating_cost_leg3 = calculate_flight_time(stop2_data['lon'], stop2_data['lat'], dest_data['lon'], dest_data['lat'])
                        total_distance_nm += distance_leg3
                        total_flight_time += flight_time_leg3
                        total_operating_cost += operating_cost_leg3

                    else:
                        # Calculate distance and time for stop1 to destination
                        distance_leg3 = haversine_distance_nm(stop1_data['lat'], stop1_data['lon'], dest_data['lat'], dest_data['lon'])
                        flight_time_leg3, operating_cost_leg3 = calculate_flight_time(stop1_data['lon'], stop1_data['lat'], dest_data['lon'], dest_data['lat'])
                        total_distance_nm += distance_leg3
                        total_flight_time += flight_time_leg3
                        total_operating_cost += operating_cost_leg3

                else:
                    # Calculate distance and time for origin to destination
                    total_flight_time, total_operating_cost = calculate_flight_time(origin_data['lon'], origin_data['lat'], dest_data['lon'], dest_data['lat'])
                    total_distance_nm = distance_nm

            else:
                # Direct flight, no stops
                stops = 0
                stop1 = 'None'
                stop2 = 'None'
                stop1_data = {'lat': None, 'lon': None}
                stop2_data = {'lat': None, 'lon': None}
                
                # Calculate distance and time for direct flight
                total_flight_time, total_operating_cost = calculate_flight_time(origin_data['lon'], origin_data['lat'], dest_data['lon'], dest_data['lat'])
                total_distance_nm = distance_nm

            # Simulate layover and calculate maintenance cost
            layover_time, maintenance_cost = simulate_layover(stops, total_flight_time, total_operating_cost)

            # Random number of passengers (20 to 204)
            passengers = random.randint(20, 204)

            # Calculate income for the flight
            ticket_price = 384.85  # Ticket price from Bureau of Transportation
            flight_income = ticket_price * passengers

            # Calculate net profit
            net_profit = flight_income - (maintenance_cost + total_operating_cost)

            # Calculate total passenger miles
            passenger_miles = passengers * total_distance_nm
            total_passenger_miles += passenger_miles

            # Prepare route data
            route_data = {
                'Route': route_id,
                'Origin': origin_code,
                'Origin_Latitude': origin_data['lat'],
                'Origin_Longitude': origin_data['lon'],
                'Destination': dest_code,
                'Destination_Latitude': dest_data['lat'],
                'Destination_Longitude': dest_data['lon'],
                'Stops': stops,
                'Stop1': stop1,
                'Stop1_Latitude': stop1_data['lat'],
                'Stop1_Longitude': stop1_data['lon'],
                'Stop2': stop2,
                'Stop2_Latitude': stop2_data['lat'],
                'Stop2_Longitude': stop2_data['lon'],
                'Passengers': passengers,
                'Distance_Nautical_Miles': total_distance_nm,
                'Flight_Time': total_flight_time,
                'Operating_Cost': total_operating_cost,
                'Layover_Time': layover_time,
                'Maintenance_Cost': maintenance_cost,
                'Flight_Income': flight_income,
                'Net_Profit': net_profit,
                'Passenger_Miles': passenger_miles
            }
            
            # Append route data to routes list
            routes.append(route_data)
            route_id += 1
            
# Write data to a text file
with open('flights.txt', 'w') as file:
    for route in routes:
        file.write(f"Flight: {route['Route']}\n")
        file.write(f"Flight Path: {route['Origin']}, {route['Stop1']}, {route['Stop2']}, {route['Destination']}\n")
        file.write(f"Origin: {route['Origin']}\n")
        file.write(f"Origin Coordinates: {route['Origin_Latitude']}, {route['Origin_Longitude']}\n")
        file.write(f"Destination: {route['Destination']}\n")
        file.write(f"Destination Coordinates: {route['Destination_Latitude']}, {route['Destination_Longitude']}\n")
        file.write(f"Stops: {route['Stops']}\n")
        if route['Stop1'] != 'None':
            file.write(f"Stop1: {route['Stop1']}\n")
            file.write(f"Stop1 Coordinates: {route['Stop1_Latitude']},{route['Stop1_Longitude']}\n")
        else:
            file.write(f"Stop1: {route['Stop1']}\n")
        if route['Stop2'] != 'None':
            file.write(f"Stop2: {route['Stop2']}\n")
            file.write(f"Stop2 Coordinates: {route['Stop2_Latitude']},{route['Stop2_Longitude']}\n")
        else:
            file.write(f"Stop2: {route['Stop2']}\n")
        file.write(f"Passengers: {route['Passengers']}\n")
        file.write(f"Distance (Nautical Miles): {route['Distance_Nautical_Miles']:.2f}\n")
        file.write(f"Flight Time (Hours): {route['Flight_Time']:.2f}\n")
        file.write(f"Operating Cost: ${route['Operating_Cost']:.2f}\n")
        file.write(f"Layover Time (Hours): {route['Layover_Time']:.2f}\n")
        file.write(f"Maintenance Cost: ${route['Maintenance_Cost']:.2f}\n")
        file.write(f"Income of Flight: ${route['Flight_Income']:.2f}\n")
        file.write(f"Net Profit of the Flight: ${route['Net_Profit']:.2f}\n")
        file.write(f"Total Passenger Miles: {route['Passenger_Miles']:.2f} passenger miles.\n")
        file.write("\n")

print("All possible flight routes data generated and saved to flights.txt")
