# Flight Simulation and Optimization Project

## Overview

This project simulates imaginary flight routes and visualizes these routes on a map of the continental United States. The simulation generates various flight paths, including routes with one or two stops, and calculates various metrics for each route, such as flight time, operational cost, maintenance cost, and net profit. The goal is to optimize flight routes by identifying and replacing "bad" routes and adjusting other routes as needed.

## Features

- **Flight Data Generation**: Generates simulated flight routes with varying numbers of stops between airports in the United States. Each flight includes details such as the origin, destination, stops, number of passengers, distance, flight time, and costs. This data is saved to `flights.txt`.

- **Flight Path Visualization**: Visualizes the flight routes on a map using Matplotlib and Cartopy. The map displays airport locations and flight paths, with an animation that shows each route and updates in real-time. This functionality is implemented in `airport_sim.py`.

- **Optimization**: Evaluates and optimizes flight routes by calculating total costs and adjusting routes based on various criteria, such as operational costs and layover times. [Optimization Program WIP]

## Files

- **`flights.txt`**: Contains simulated flight route data, including origin, destination, stops, and various metrics for each route.

- **`airports.txt`**: Contains information about airports, including IATA codes, names, populations, longitudes, and latitudes.

- **`flight_generator`**: Produces the imaginary flights and saves them into `flights.txt`.

- **`airport_sim.py`**: Contains the visualization and plotting of these imaginary flights.

- **[Optimization Program WIP]**: Work in progress for optimizing flight routes.

## Instructions

1. **Prepare Data Files**: Ensure that `airports.txt` and `flights.txt` are available in the same directory as the script.

2. **Generate Flight Data**: Use the `flight_generator` to create the flight routes and save them to `flights.txt`.

3. **Run the Visualization**: Execute `airport_sim.py` to generate and visualize the flight paths on the map.

4. **Optimization**: The optimization program is currently a work in progress and will be updated to include functionality for route optimization.