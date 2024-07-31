#!/usr/bin/env python3

"""Visualization and Anayzing of the Levels of Optimizations"""

import matplotlib.pyplot as plt
from flight_utils import *

# Step 1: Load and parse the data
def load_flights(file_path):
    return load_flights_newstyle(file_path)

# Step 2: Calculate total passenger miles
def calculate_total_passenger_miles(flights):
    total_passenger_miles = 0
    for flight in flights:
        flight_path = flight_path2city_list(flight['flight_path'])
        distance = calc_distance_new(flight_path)
        passengers = int(flight['passengers'])
        passenger_miles = passengers * distance
        total_passenger_miles += passenger_miles
    return total_passenger_miles

# Step 3: Calculate total net profit
def calculate_income(record):
    """Calculate the income from a flight record based on the number of passengers and average ticket price."""
    avg_ticket_price = 384.85  # Average ticket price in dollars
    passengers = int(record['passengers'])
    income = avg_ticket_price * passengers
    return income

def calculate_total_net_profit(flights):
    total_revenue = 0
    total_operational_cost = 0
    
    for flight in flights:
        flight_path = flight_path2city_list(flight['flight_path'])
        distance = calc_distance_new(flight_path)
        passengers = int(flight['passengers'])
        
        # Calculate revenue using the new function
        income = calculate_income(flight)
        total_revenue += income
        
        # Calculate operational cost
        for i in range(len(flight_path) - 1):
            origin = flight_path[i]
            destination = flight_path[i + 1]
            lat1, lon1 = airports[origin]['lat'], airports[origin]['lon']
            lat2, lon2 = airports[destination]['lat'], airports[destination]['lon']
            _, operational_cost = calculate_flight_time(lon1, lat1, lon2, lat2)
            total_operational_cost += operational_cost

    total_net_profit = total_revenue - total_operational_cost
    return total_net_profit

# Step 4: Calculate the total number of passengers
def calculate_total_passengers(flights):
    total_passengers = 0
    for flight in flights:
        total_passengers += int(flight['passengers'])
    return total_passengers

# Files to be processed
files = ['generated_flights_new.txt', 'sorted_flights_new.txt', 'profitable_flights.txt']

# Store results
results = []

for file in files:
    flights = load_flights(file)
    total_passenger_miles = calculate_total_passenger_miles(flights)
    total_net_profit = calculate_total_net_profit(flights)
    total_passengers = calculate_total_passengers(flights)
    results.append((file, total_passenger_miles, total_net_profit, total_passengers))

# Step 5: Plot the data
labels, passenger_miles, net_profits, total_passengers = zip(*results)

x = range(len(labels))

fig, ax1 = plt.subplots()

# Create secondary axes
ax2 = ax1.twinx()
ax3 = ax1.twinx()

# Offset the third y-axis
ax3.spines['right'].set_position(('outward', 60))

# Plot the data
bar_width = 0.2
bar_positions = [i - bar_width for i in x]

ax1.bar(bar_positions, passenger_miles, width=bar_width, color='g', label='Passenger Miles')
ax2.bar([i for i in x], net_profits, width=bar_width, color='b', label='Net Profit')
ax3.bar([i + bar_width for i in x], total_passengers, width=bar_width, color='r', label='Total Passengers')

# Labeling
ax1.set_xlabel('Files')
ax1.set_ylabel('Total Passenger Miles', color='g')
ax2.set_ylabel('Total Net Profit ($)', color='b')
ax3.set_ylabel('Total Passengers', color='r')

ax1.set_xticks([i for i in x])
ax1.set_xticklabels(labels)

# Add legends
ax1.legend(loc='upper left')
ax2.legend(loc='upper center')
ax3.legend(loc='upper right')

fig.tight_layout()
plt.title('Total Passenger Miles, Net Profit, and Number of Passengers per File')
plt.show()
