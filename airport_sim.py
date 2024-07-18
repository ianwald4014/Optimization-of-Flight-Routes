#! /usr/bin/env python3

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation

class FlightSimulation: 
    def read_flights(self, filename): # Reads flights.txt
        flight_data = []
        with open(filename, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith("Flight Path:"):
                flight_path = line.split(":")[1].strip().split(", ") # Reads the flight path from left to right 
                flight_data.append(flight_path)
        return flight_data

    def read_airports(self, filename): # Reads airports.txt
        airports = {}
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(', ')
                if len(parts) == 5:
                    try:
                        code, name, population, lon, lat = parts
                        airports[code.strip()] = (float(lon), float(lat))
                    except ValueError as e:
                        print(f"Error processing line {line}: {e}")
                else:
                    print(f"Issue with line format: {line}")
        return airports

    def create_map(self, airports):
        fig, ax = plt.subplots(figsize=(45,45), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
        ax.add_feature(cfeature.COASTLINE, edgecolor='black')
        ax.set_extent([-130, -65, 20, 50], crs=ccrs.PlateCarree())

        for code, (lon, lat) in airports.items():
            ax.text(lon, lat, code, fontsize=8, ha='center', transform=ccrs.PlateCarree())
            ax.plot(lon, lat, 'o', markersize=5, transform=ccrs.PlateCarree())

        return fig, ax

    def animate_flight_path(self, airports, fig, ax, flight_data):
        def update(frame):
            ax.clear()
            ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
            ax.add_feature(cfeature.COASTLINE, edgecolor='black')
            ax.set_extent([-130, -65, 20, 50], crs=ccrs.PlateCarree())

            for code, (lon, lat) in airports.items():
                ax.text(lon, lat, code, fontsize=8, ha='center', transform=ccrs.PlateCarree())
                ax.plot(lon, lat, 'o', markersize=5, transform=ccrs.PlateCarree())

            flight_idx = frame // 3
            sub_frame = frame % 3

            # Plot all previously plotted paths
            for prev_idx in range(len(flight_data)):
                if prev_idx < flight_idx:
                    flight_path = flight_data[prev_idx]
                    coordinates = [airports.get(airport) for airport in flight_path if airports.get(airport)]
                    if len(coordinates) > 1:
                        for i in range(len(coordinates) - 1):
                            ax.plot([coordinates[i][0], coordinates[i + 1][0]], [coordinates[i][1], coordinates[i + 1][1]], color='red', transform=ccrs.PlateCarree())

            # Plot the current path
            if flight_idx < len(flight_data):
                flight_path = flight_data[flight_idx]
                coordinates = [airports.get(airport) for airport in flight_path if airports.get(airport)]
                
                if len(coordinates) > 1:
                    if sub_frame < len(coordinates) - 1:
                        start = coordinates[sub_frame]
                        end = coordinates[sub_frame + 1]
                        ax.plot([start[0], end[0]], [start[1], end[1]], color='red', transform=ccrs.PlateCarree()) # Associating location as a coordinate,.
                    
                    # Plot the entire path for the current flight path
                    for i in range(len(coordinates) - 1):
                        ax.plot([coordinates[i][0], coordinates[i + 1][0]], [coordinates[i][1], coordinates[i + 1][1]], color='red', transform=ccrs.PlateCarree())

                flight_path_str = " to ".join(flight_path)
                ax.set_title(f'Flight {flight_idx + 1}: {flight_path_str} - Frame {frame}', fontsize=16)

        total_frames = len(flight_data) * 3
        ani = FuncAnimation(fig, update, frames=range(total_frames), interval= 750, repeat=False)
        plt.show()

def main():
    sim = FlightSimulation()
    airports_filename = 'airports.txt'
    airports = sim.read_airports(airports_filename)

    flights_filename = 'flights.txt'
    flight_data = sim.read_flights(flights_filename)
    
    fig, ax = sim.create_map(airports)

    sim.animate_flight_path(airports, fig, ax, flight_data)

if __name__ == '__main__':
    main()

