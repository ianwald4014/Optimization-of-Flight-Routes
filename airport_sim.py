import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class FlightSimulation:
    def __init__(self):
        self.total_passengers = 0
        self.total_cost = 0
        self.total_time = 0.0

    def read_flights(self, filename):
        flight_data = {}
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            for line in lines:
                if line.startswith("Flight:"):
                    flight_number = int(line.split(":")[1].strip())
                    flight_data[flight_number] = {}
                elif line.startswith("Origin:"):
                    origin_line = line.split(":")[1].strip()
                    origin_parts = origin_line.split("Lat:")
                    flight_data[flight_number]['origin'] = origin_parts[0].split()[0]
                    if len(origin_parts) > 1:
                        origin_lon_lat = origin_parts[1].split(",")
                        if len(origin_lon_lat) >= 2:
                            flight_data[flight_number]['origin_coordinates'] = (
                                float(origin_lon_lat[1].strip()),  # Latitude
                                float(origin_lon_lat[0].strip())   # Longitude
                            )
                elif line.startswith("Destination:"):
                    destination_line = line.split(":")[1].strip()
                    destination_parts = destination_line.split("Lat:")
                    flight_data[flight_number]['destination'] = destination_parts[0].split()[0]
                    if len(destination_parts) > 1:
                        destination_lon_lat = destination_parts[1].split(",")
                        if len(destination_lon_lat) >= 2:
                            flight_data[flight_number]['destination_coordinates'] = (
                                float(destination_lon_lat[1].strip()),  # Latitude
                                float(destination_lon_lat[0].strip())   # Longitude
                            )
                elif line.startswith("Stops:"):
                    flight_data[flight_number]['stops'] = int(line.split(":")[1].strip())
                elif line.startswith("Stop1:"):
                    stop1_line = line.split(":")[1].strip()
                    stop1_parts = stop1_line.split("Lat:")
                    if len(stop1_parts) > 1:
                        stop1_lon_lat = stop1_parts[1].split(",")
                        if len(stop1_lon_lat) >= 2:
                            flight_data[flight_number]['stop1_coordinates'] = (
                                float(stop1_lon_lat[1].strip()),  # Latitude
                                float(stop1_lon_lat[0].strip())   # Longitude
                            )
                elif line.startswith("Stop2:"):
                    stop2_line = line.split(":")[1].strip()
                    stop2_parts = stop2_line.split("Lat:")
                    if len(stop2_parts) > 1:
                        stop2_lon_lat = stop2_parts[1].split(",")
                        if len(stop2_lon_lat) >= 2:
                            flight_data[flight_number]['stop2_coordinates'] = (
                                float(stop2_lon_lat[1].strip()),  # Latitude
                                float(stop2_lon_lat[0].strip())   # Longitude
                            )
                elif line.startswith("Passengers:"):
                    flight_data[flight_number]['passengers'] = int(line.split(":")[1].strip())
                elif line.startswith("Distance (Nautical Miles):"):
                    flight_data[flight_number]['distance'] = float(line.split(":")[1].strip())
                elif line.startswith("Flight Time (Hours):"):
                    flight_data[flight_number]['flight_time'] = float(line.split(":")[1].strip())
                elif line.startswith("Operating Cost:"):
                    flight_data[flight_number]['operating_cost'] = float(line.split(":")[1].strip().replace('$', ''))
                elif line.startswith("Layover Time (Hours):"):
                    flight_data[flight_number]['layover_time'] = float(line.split(":")[1].strip())
                elif line.startswith("Maintenance Cost:"):
                    flight_data[flight_number]['maintenance_cost'] = float(line.split(":")[1].strip().replace('$', ''))

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")

        return flight_data

    def read_airports(self, filename):
        airports = []
        try:
            with open(filename, 'r') as file:
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
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")

        return airports

    def create_map(self, airports):
        fig, ax = plt.subplots(figsize=(15, 15), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
        ax.add_feature(cfeature.COASTLINE, edgecolor='black')
        ax.set_extent([-130, -65, 20, 50], crs=ccrs.PlateCarree())

        for code, name, _, lon, lat in airports:
            ax.text(lon, lat, code, fontsize=8, ha='center', transform=ccrs.PlateCarree())
            ax.plot(lon, lat, 'o', markersize=5, transform=ccrs.PlateCarree())

        return fig, ax

    def animate_flight_path(self, airports, fig, ax, all_flight_data):
        def update(frame):
            ax.clear()
            ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
            ax.add_feature(cfeature.COASTLINE, edgecolor='black')
            ax.set_extent([-130, -65, 20, 50], crs=ccrs.PlateCarree())

            for code, name, _, lon, lat in airports:
                ax.text(lon, lat, code, fontsize=8, ha='center', transform=ccrs.PlateCarree())
                ax.plot(lon, lat, 'o', markersize=5, transform=ccrs.PlateCarree())

            flight_idx = frame // 3
            sub_frame = frame % 3

            if flight_idx < len(all_flight_data):
                flight = all_flight_data[flight_idx]
                origin = flight['origin']
                destination = flight['destination']
                stops = flight.get('stops', 0)
                stop1 = flight.get('stop1_coordinates', None)
                stop2 = flight.get('stop2_coordinates', None)

                path = []
                if 'origin_coordinates' in flight:
                    path.append(flight['origin_coordinates'])
                if stop1:
                    path.append(stop1)
                if stop2:
                    path.append(stop2)
                if 'destination_coordinates' in flight:
                    path.append(flight['destination_coordinates'])

                # Debug statements to verify path
                print(f'Flight {flight_idx + 1}: Origin: {origin}, Destination: {destination}, Stops: {stops}')
                print(f'  Path: {path}')

                # Draw the path segments
                if sub_frame == 0 and len(path) >= 2:
                    lons, lats = zip(*path[:2])
                    ax.plot(lons, lats, color='blue', marker='o', transform=ccrs.PlateCarree())
                elif sub_frame == 1 and len(path) >= 3:
                    lons, lats = zip(*path[:3])
                    ax.plot(lons, lats, color='blue', marker='o', transform=ccrs.PlateCarree())
                elif sub_frame == 2 and len(path) == 4:
                    lons, lats = zip(*path)
                    ax.plot(lons, lats, color='blue', marker='o', transform=ccrs.PlateCarree())

                ax.set_title(f'Flight {flight_idx + 1}\n {origin} - {destination}\n Stops: {stops}')

        total_frames = len(all_flight_data) * 3
        ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000, repeat=False)
        plt.show()

    def run_simulation(self, airports_file, flights_file):
        airports = self.read_airports(airports_file)
        flight_data = self.read_flights(flights_file)
        if flight_data:
            fig, ax = self.create_map(airports)
            all_flight_data = [flight_data[key] for key in sorted(flight_data.keys())]
            self.animate_flight_path(airports, fig, ax, all_flight_data)

if __name__ == "__main__":
    simulation = FlightSimulation()
    simulation.run_simulation('airports.txt', 'flights.txt')
