import matplotlib.pyplot as plt
import networkx as nx
import random
import time
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.distance import geodesic
from matplotlib.animation import FuncAnimation

class FlightSimulation:
    def __init__(self):
        self.total_passengers = 0
        self.total_cost = 0
        self.total_time = 0
        self.round_trips = []
        self.current_time = 0.0

    def parameters(self, filename):
        with open('filename', 'r') as file:
            lines = file.readlines()

        flight_data = {}

        for lines in lines:  # Need to make sure section reads all 90 flights 
            if line.startswith("Flight:"):
                flight_number = int(line.split(":")[1].strip())
                flight_data[flight_number] = {}
            elif line.startswith("Origin:"):
                flight_data[flight_number]['origin'] = line.split(":")[1].strip().split()[0]
            elif line.startswith("Destination:"):
                flight_data[flight_number]['destination'] = line.split(":")[1].strip().split()[0]
            elif line.startswith("Stops:"):
                flight_data[flight_number]['stops'] = int(line.split(":")[1].strip())
            elif line.startswith("Stop1:"):
                stop1 = line.split(":")[1].strip().split()[0]
                if stop1 != "None":
                    flight_data[flight_number]['stop1'] = stop1
            elif line.startswith("Stop2:"):
                stop2 = line.splt(":")[1].strip().split()[0]
                if stop2 != "None":
                    flight_data[flight_number]['stop2'] = stop2
            elif line.startswith("Passengers:"):
                flight_data[flight_number]['passengers']= int(line.split(":")[1]strip())
            elif line.startswith("Distance (Nautical Miles:"):
                flight_data[flight_number]['distance_nm)'] = float(line.split(":")[1].strip())
            elif line.startswith("Flight Time (Hours)"):
                flight_data[flight_number]['flight_time' = float(line.split(":")[1].strip())
            elif line.startswith("Maintenance Flight Hour:"):
                flight_data[flight_number]['maintenance_flight_hour'] = float(line.split(":")[1].strip())
            elif line.startswith("Layover Time (Hours):"): # AOI if/else statement later
                flight_data[flight_number]['layover_time'] = float(line.split(":")[1].strip())
            elif line.startswith("Maintenance Cost:"):
                flight_data[flight_number]['maintenance_cost'] = float(line.split(": $")[1].strip())
            elif line.startswith("Income of Flight:"):
                flight_data[flight_number]['flight_income'] = float(line.split(": $")[1].strip()))
            elif line.startswith("Net Profit of the Flight:"):
                flight_data[flight_number]['net_profit'] = float(line.split(": $")[1].strip())
            elif line.startswith("Total Passenger Miles:"):
                flight_data[flight_number]['total_passenger_miles'] = float(line.split(":")[1].strip())
