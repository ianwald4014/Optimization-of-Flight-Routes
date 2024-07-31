#! /usr/bin/env python3

import random
from math import radians, sin, cos, sqrt, atan2

from flight_utils import *

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

def main():
    # Initialize variables
    routes = []
    route_id = 1
    total_passenger_miles = 0

    # Generate all possible routes
    for origin_code, origin_data in airports.items():
        for dest_code, dest_data in airports.items():
            if origin_code == dest_code:  # Ensure origin and destination are different
                continue

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
            net_profit = flight_income - maintenance_cost

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

    # write new format alongside old one
    fname = 'generated_flights_new.txt'
    write_flights_oldstyle2newstyle(fname, routes)
            
    # Write data to a text file
    with open('flights.txt', 'w') as fp:
        for route in routes:
            # append_route(fp, route)
            fp.write(f"Flight: {route['Route']}\n")
            fp.write(f"Flight Path: {route['Origin']}, {route['Stop1']}, {route['Stop2']}, {route['Destination']}\n")
            fp.write(f"Origin: {route['Origin']}\n")
            fp.write(f"Origin Coordinates: {route['Origin_Latitude']}, {route['Origin_Longitude']}\n")
            fp.write(f"Destination: {route['Destination']}\n")
            fp.write(f"Destination Coordinates: {route['Destination_Latitude']}, {route['Destination_Longitude']}\n")
            fp.write(f"Stops: {route['Stops']}\n")
            if route['Stop1'] != 'None':
                fp.write(f"Stop1: {route['Stop1']}\n")
                fp.write(f"Stop1 Coordinates: {route['Stop1_Latitude']},{route['Stop1_Longitude']}\n")
            else:
                fp.write(f"Stop1: {route['Stop1']}\n")
            if route['Stop2'] != 'None':
                fp.write(f"Stop2: {route['Stop2']}\n")
                fp.write(f"Stop2 Coordinates: {route['Stop2_Latitude']},{route['Stop2_Longitude']}\n")
            else:
                fp.write(f"Stop2: {route['Stop2']}\n")
            fp.write(f"Passengers: {route['Passengers']}\n")
            fp.write(f"Distance (Nautical Miles): {route['Distance_Nautical_Miles']:.2f}\n")
            fp.write(f"Flight Time (Hours): {route['Flight_Time']:.2f}\n")
            fp.write(f"Operating Cost: ${route['Operating_Cost']:.2f}\n")
            fp.write(f"Layover Time (Hours): {route['Layover_Time']:.2f}\n")
            fp.write(f"Maintenance Cost: ${route['Maintenance_Cost']:.2f}\n")
            fp.write(f"Income of Flight: ${route['Flight_Income']:.2f}\n")
            fp.write(f"Net Profit of the Flight: ${route['Net_Profit']:.2f}\n")
            fp.write(f"Total Passenger Miles: {route['Passenger_Miles']:.2f} passenger miles.\n")
            fp.write("\n")
    print("All possible flight routes data generated and saved to flights.txt")


if __name__ == '__main__':
    main()
