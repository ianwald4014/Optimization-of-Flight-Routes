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

    def parameters(self):
        origin = 'JFK'
        destination = 'LAX'
        stop_cities = ['DFW', 'ABQ'] # Refer to airports.txt IATA codes. Order the cities from first to last
        return origin, destination, stop_cities

    def read_airports(self, filename):
        airports = []
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

    def calculate_flight_time(self, lon1, lat1, lon2, lat2):
        distance_nm = geodesic((lat1, lon1), (lat2, lon2)).nautical
        speed_knots = 485 
        flight_time = distance_nm / speed_knots
        maintenance_flight_hour = 5757 * flight_time
        return flight_time, maintenance_flight_hour

    def simulate_layover(self, flight_time, maintenance_flight_hour):
        layover_time = random.uniform(1, 2.0)
        maintenance_cost_per_hour = random.uniform(32.18, 150)
        maintenance_cost = (layover_time * maintenance_cost_per_hour) + maintenance_flight_hour
        return layover_time, maintenance_cost

    def simulate_passengers(self, pop_ratio, max_passengers=204):
        return min(int(pop_ratio * max_passengers), max_passengers)

    def animate_flight_path(self, airports, fig, ax, origin, destination, stop_cities):
        G = nx.Graph()

        airports_sorted = sorted(airports, key=lambda x: x[2], reverse=True)

        for code, name, population, lon, lat in airports_sorted:
            G.add_node(code, pos=(lon, lat), population=population)

        self.total_passengers = 0
        self.total_cost = 0
        self.total_time = 0
        round_trip = [origin]

        round_trip.extend(stop_cities)
        round_trip.append(destination)
        round_trip.append(origin)

        self.round_trips = []

        def update(frame):
            ax.clear()
            ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
            ax.add_feature(cfeature.COASTLINE, edgecolor='black')
            ax.set_extent([-130, -65, 20, 50], crs=ccrs.PlateCarree())

            for code, name, _, lon, lat in airports:
                ax.text(lon, lat, code, fontsize=8, ha='center', transform=ccrs.PlateCarree())
                ax.plot(lon, lat, 'o', markersize=5, transform=ccrs.PlateCarree())

            pos = nx.get_node_attributes(G, 'pos')

            if frame < len(round_trip):
                origin = 'origin'
                destination = 'destination'
                a, b = round_trip[frame - 1], round_trip[frame]
                pop_ratio_a = G.nodes[a]['population'] / sum(airport[2] for airport in airports_sorted)
                pop_ratio_b = G.nodes[b]['population'] / sum(airport[2] for airport in airports_sorted)
                passengers_a = self.simulate_passengers(pop_ratio_a)
                passengers_b = self.simulate_passengers(pop_ratio_b)
                self.total_passengers += max(passengers_a, passengers_b)
                flight_time, maintenance_flight_hour = self.calculate_flight_time(*pos[a], *pos[b])
                layover_time, maintenance_cost = self.simulate_layover(flight_time, maintenance_flight_hour)
            
                self.current_time += flight_time + layover_time
                self.total_time += flight_time + layover_time
                self.total_cost += maintenance_cost

                self.round_trips.append({
                    'origin': a,
                    'destination': b,
                    'total_passengers': self.total_passengers,
                    'total_cost': self.total_cost,
                    'total_time': self.total_time,
                    'layover_time': layover_time,
                    'flight_time': flight_time
                })

                if origin == destination:
                    nx.clear()
                else:
                    nx.draw_networkx_edges(G, pos, edgelist=[(a, b)], edge_color='red', ax=ax)

                ax.set_title(f'Flight - Frame {frame}\nTotal Passengers: {self.total_passengers}\nTotal Cost: ${self.total_cost:.2f}\nTotal Time: {self.current_time:.2f} hours\nNumber of Stops: {len(stop_cities)}')

                if frame == len(round_trip) - 1:
                    with open('flights.txt', 'w') as f:
                        for trip in self.round_trips:
                            origin = trip['origin']
                            destination = trip['destination']
                            total_passengers = trip['total_passengers']
                            total_cost = trip['total_cost']
                            total_time = trip['total_time']
                            flight_time = trip['flight_time']
                            layover_time = trip.get('layover_time', None)

                            if origin == destination:
                                f.write(f'Layover at {origin}\n')
                                f.write(f'Total Passengers: {total_passengers}\n')
                                f.write(f'Total Cost: ${total_cost:,.2f}\n')
                                f.write(f'Total Time: {total_time:.2f} hours\n')
                                f.write(f'Time of Layover: {layover_time:.2f} hours \n\n')
                            else:
                                f.write(f'Flight: Trip from {origin} to {destination}\n')
                                f.write(f'Total Passengers: {total_passengers}\n')
                                f.write(f'Total Cost: ${total_cost:,.2f}\n')
                                f.write(f'Total Time: {total_time:.2f} hours\n')
                                f.write(f'Flight Time: {flight_time:.2f} hours \n\n')

        ani = FuncAnimation(fig, update, frames=range(1, len(round_trip)), interval=600, repeat=False)
        plt.show()

def main():
    sim = FlightSimulation()
    filename = 'airports.txt'
    airports = sim.read_airports(filename)

    origin, destination, stop_cities = sim.parameters()
    
    fig, ax = sim.create_map(airports)

    sim.animate_flight_path(airports, fig, ax, origin, destination, stop_cities)

if __name__ == '__main__':
    main()
