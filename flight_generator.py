import random
from geopy.distance import geodesic

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

def calculate_flight_time(lon1, lat1, lon2, lat2):
    """Calculate flight time and maintenance flight hour."""
    distance_nm = geodesic((lat1, lon1), (lat2, lat2)).nautical
    speed_knots = 485  # Average speed of a Boeing 737 MAX in knots
    flight_time = distance_nm / speed_knots
    operational_cost  = 5757 * flight_time
    return flight_time, operational_cost

def simulate_layover(stops, flight_time, operational_cost):
    """Simulate layover time and calculate maintenance cost."""
    if stops == 0:
        layover_time = 0
        maintenance_cost = operational_cost
    else:
        layover_time = random.uniform(1, 2.0)  # Layover time in hours
        maintenance_cost_per_hour = random.uniform(32.18, 150)  # Maintenance cost per hour
        maintenance_cost = (layover_time * maintenance_cost_per_hour) + operational_cost
    
    return layover_time, maintenance_cost

# Generate all possible routes
routes = []
route_id = 1
total_passenger_miles = 0

# Consider all combinations of origin and destination airports
for origin_code, origin_data in airports.items():
    for dest_code, dest_data in airports.items():
        if origin_code != dest_code:  # Ensure origin and destination are different
            # Calculate distance and flight time
            distance_nm = geodesic((origin_data['lat'], origin_data['lon']), (dest_data['lat'], dest_data['lon'])).nautical
            
            # Determine number of stops based on distance
            if distance_nm > 434.488:  # 500 miles in nautical miles
                stops = random.randint(0, 2)
                stop_cities = random.sample(list(airports.keys()), stops)
                stop1 = stop_cities[0] if stops >= 1 else 'None'
                stop2 = stop_cities[1] if stops >= 2 else 'None'
            else:
                stops = 0
                stop1 = 'None'
                stop2 = 'None'
            
            # Random number of passengers (1 to 204)
            passengers = random.randint(20, 204)
            
            # Calculate flight time and maintenance cost
            flight_time, operational_cost  = calculate_flight_time(origin_data['lon'], origin_data['lat'], dest_data['lon'], dest_data['lat'])
            layover_time, maintenance_cost = simulate_layover(stops, flight_time, operational_cost)
                       
            # Calculate income for the flight
            ticket_price = 384.85  # Ticket price from Bureau of Transportation
            flight_income = ticket_price * passengers * 90  # Number of flights

            # Calculate the net profit
            net_profit = flight_income - (maintenance_cost + operational_cost)
            
            # Calculate total passenger miles
            passenger_miles = passengers * distance_nm
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
                'Stop2': stop2,
                'Passengers': passengers,
                'Distance_Nautical_Miles': distance_nm,
                'Flight_Time': flight_time,
                'Operational_Cost': operational_cost,
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
        file.write(f"Origin: {route['Origin']} (Lat: {route['Origin_Latitude']}, Lon: {route['Origin_Longitude']})\n")
        file.write(f"Destination: {route['Destination']} (Lat: {route['Destination_Latitude']}, Lon: {route['Destination_Longitude']})\n")
        file.write(f"Stops: {route['Stops']}\n")
        file.write(f"  Stop1: {route['Stop1']}\n")
        file.write(f"  Stop2: {route['Stop2']}\n")
        file.write(f"Passengers: {route['Passengers']}\n")
        file.write(f"Distance (Nautical Miles): {route['Distance_Nautical_Miles']:.2f}\n")
        file.write(f"Flight Time (Hours): {route['Flight_Time']:.2f}\n")
        file.write(f"Operational Cost: ${route['Operational_Cost']:.2f}\n")
        file.write(f"Layover Time (Hours): {route['Layover_Time']:.2f}\n")
        file.write(f"Maintenance Cost: ${route['Maintenance_Cost']:.2f}\n")
        file.write(f"Income of Flight: ${route['Flight_Income']:.2f}\n")
        file.write(f"Net Profit of the Flight: ${route['Net_Profit']:.2f}\n")
        file.write(f"Total Passenger Miles: {route['Passenger_Miles']:.2f} passenger miles. \n")
        file.write("\n")

print("All possible flight routes data generated and saved to flights.txt")
