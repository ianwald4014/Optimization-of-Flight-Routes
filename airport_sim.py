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
            elif line.startswith("Operational Cost:"):
                flight_data[flight_number]['operational_cost'] = float(line.split(": $")[1].strip()) # AOI
            elif line.startswith("Layover Time (Hours):"): # AOI if/else statement later
                flight_data[flight_number]['layover_time'] = float(line.split(":")[1].strip())
            elif line.startswith("Maintenance Cost:"):
                flight_data[flight_number]['maintenance_cost'] = float(line.split(": $")[1].strip()) # AOI 
            elif line.startswith("Income of Flight:"):
                flight_data[flight_number]['flight_income'] = float(line.split(": $")[1].strip())) # AOI 
            elif line.startswith("Net Profit of the Flight:"):
                flight_data[flight_number]['net_profit'] = float(line.split(": $")[1].strip()) # AOI 
            elif line.startswith("Total Passenger Miles:"):
                flight_data[flight_number]['total_passenger_miles'] = float(line.split(":")[1].strip()) # AOI 

            # Just using the first flight data for now; will adjust for other 89 flights
            first_flight_data = list(flight_data.values())[0]
            origin = first_flight_data['origin']
            destination = first_flight_data['destination']
            stop_cities = []
            if 'stop1' in first_flight_data:
                stop_cities.append(first_flight_data['stop1'])
            if 'stop2' in first_flight_data:
                stop_cities.append(first_flight_data['stop2'])

    # Recycle from orignal plotting code
    def read_airports(self, filename):
        airports = []
        with open(filename, 'r') as file:  # To open airports.txt
            for line in file:
                parts = line.strip().split(', ')
                if len(parts) == 5:
                    try:
                        code, name, population, lon, lat = parts
                        airports.append((code.strip(), name.strip(), int(population), float(lon), float(lat)))  
                    except ValueError as e:
                        print(f"Error processing line {line}: {e}")
                    else:
                        print(f"Issue with line format: {line}")
                    return airports
                
    def create_map(self, airports):
        fig, ax = plt.subplots(figsize=(30, 30), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
        ax.add_feature(cfeature.COASTLINE, edgecolor='black')
        ax.set_extent([-130, -65, 20, 50], crs=ccrs.PlateCarree())
    
        for code, name, _, lon, lat in airports:
            ax.text(lon, lat, code, fontsize=8, ha='center', transform=ccrs.PlateCarree())
            ax.plot(lon, lat, 'o', markersize=5, transform=ccrs.PlateCarree())

    return fig, ax

    

        

    
