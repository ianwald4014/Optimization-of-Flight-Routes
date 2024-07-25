# Flight Simulation and Optimization Project

## Overview

This project simulates imaginary flight routes and visualizes these routes on a map of the continental United States. The simulation generates various flight paths, including routes with one or two stops, and calculates metrics such as flight time, operational cost, maintenance cost, and net profit. The goal is to optimize flight routes by identifying and replacing "bad" routes and adjusting others as needed.

## Prerequisites

Before running the scripts, make sure you have the following Python modules installed:

- **geopy**: Used for geocoding and distance calculations.
- **cartopy**: Used for map visualization.
- **matplotlib**: Required for plotting.

You can install these modules using pip:

```pip install geopy cartopy matplotlib```

## Features

- **Flight Data Generation**: Creates simulated flight routes with details such as origin, destination, stops, passengers, distance, flight time, and costs. Data is saved to `flights.txt`.

- **Flight Path Visualization**: Uses Matplotlib and Cartopy to display flight routes and airport locations on a map, with real-time updates. Implemented in `airport_sim.py`.

- **Optimization**: Evaluates and optimizes flight routes based on criteria like cost and layovers. [Work in Progress]

## Files

- **`flights.txt`**: Contains simulated flight route data.

- **`airports.txt`**: Contains airport information.

- **`flight_generator.py`**: Generates flight data and saves it to `flights.txt`.

- **`airport_sim.py`**: Visualizes flight routes on a map.

- **`flight_sorting_optimization.py`**: Optimizes flight routes from `flights.txt` using the haversine formula and saves to `sorted_flights.txt`.

- **`flight_optimization.py`**: In development for further route optimization.

## Instructions

1. **Prepare Data Files**: Ensure that `airports.txt` and `flights.txt` are available in the same directory as `flight_generator.py`, `flight_sorting_optimization.py`, and `airport_sim.py`.

2. **Generate Flight Data**: Run ```python3 flight_generator.py``` in a terminal and view `flights.txt` in your preferred editor and/or running either a ```cat flights.txt``` or ```less flights.txt``` in your terminal.

3. **Optional: Run the Visualization**: Execute ```python3 airport_sim.py``` in a terminal to generate and visualize the flight paths on the map.

4. **Optimize the Flight Routes:** Once the flights have been generated in `flights.txt`, create a file labeled as `sorted_flights.txt.`

5. **Optimize the Flight Routes [Continued]:** Run `python3 flight_sorting_optimization.py` in the terminal and saves the output into `sorted_flights.txt`. You can view `sorted_flights.txt` via an editor or executing in the terminal ```cat flights.txt``` or ```less flights.txt```.

5. **Optional: Run the Visualization**: Open `airport_sim.py` in your preferable editor, change line 98 to ```# flights_filename = 'flights.txt'``` and change line 99 to ```flights_filename = 'sorted_flights.txt'```, saving the file. T

6. **Optional: Run the Visualization [Continued]**: Proceed to run a ```python3 airport_sim.py``` to generate `sorted_flights.txt` and visualize the flight paths on the map.

7. The second optimization program is currently a work in progress and will be updated to include functionality for route optimization.