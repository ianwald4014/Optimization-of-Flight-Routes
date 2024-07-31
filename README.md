# Flight Simulation and Optimization Project

## Overview

Simulating imaginary flight routes and visualizes these
routes on a map of the continental United States. The simulation
generates various flight routes and calculates various metrics. The goal is to optimize flight
routes by reducing distance, maximizing profitability, and to search and replacing "bad proftiable" routes.

The procedure might be seen as this flowchart:

```
GENERATE_FLIGHTS
    |
    v
SORT_FLIGHTS_BY_DISTANCE
    |
    v
OPTIMIZE_SORTED_FLIGHTS
    |
    v
REMOVE_AND_REPLACE_BAD_FLIGHTS
    |
    v
RUN_GRAPH_ANALYSIS
```

## Prerequisites

Before running the scripts, make sure you have the following Python modules installed:

- **cartopy**: Used for map visualization.
- **matplotlib**: Required for plotting.

You can install these modules using pip:

```
pip install cartopy matplotlib
```

## Features

- **Flight Data Generation**: Creates all simulated flight routes with details such as origin, destination, stops, passengers`.

- **Flight Path Visualization**: Uses Matplotlib and Cartopy to display flight routes and airport locations on a map, with real-time updates. 

- **Optimization**: Evaluates and optimizes flight routes based on criteria like profitability, passengers, and passenger miles.

## Files

- **`flights.txt`**: Contains simulated flight route data.

- **`airports.txt`**: Contains airport information.

- **`flight_generator.py`**: Generates flight data and saves it to `generated_flights_new.txt`.

- **`airport_sim.py`**: Visualizes flight routes on a map.

- **`sort_flights_by_distance.py`**: Optimizes flight routes from `generated_flights_new.txt` using the haversine formula (distance) and saves to `sorted_flights_new.txt`.

- **`flight_optimization.py`**: Optimizes flight routes by identifying all worst flights off profitability from `sorted_flights_new.txt` or `generated_flights_new.txt` and replaces with a more profitable flight
  that is in close proximity to the bad flight, while attempting to accommadating passengers from the original bad flight.

## Instructions

**Create Series Of Flights**

To generate all possible flights from a set number of airports with no optimization, run the following: 
```
python3 flight_generator.py
```

Running the command in the terminal, you can view in view the output files (`generated_flights_new.txt`) in the terminal:
 ```
 cat generated_flights_new.txt
 ```
 or
 ```
 less generated_flights_new.txt
 ```
or
 View in preferred editor.

**Optimization of the Flight Routes: Sequencing of Stops:**

With the generation of flights, the program will then optimize the flight paths and change them to reduce distance by rearranging the orders of airports in the flight path.

Once the flights have been generated in `generated_flights_new.txt` run:
```
python3 sort_flights_by_distance.py 
```

Running the command in the terminal, you can view in view the output files (`sorted_flights_new.txt`) with an editor  or the terminal with:

 ```
 cat sorted_flights_new.txt
 ```
 or
 ```
 less sorted_flights_new.txt
 ```

**Continuation of Optimization of the Flight Routes: Identify and Replace Bad Profitable Flights**

After the sorting of flight paths, this program will seek to identify all bad flights that are below a profit threshold. This program will then remove and find replacements of flights based on proximity.

With the verifiation of input files have information (`sorted_flights_new.txt` [Default] or `generated_flights_new.txt`), run the following command:

```
python3 flight_optimization.py 
```

Program is capable of generating output with different input .txt files. These instances can be seen with,

```
python3 flight_optimization.py sorted_flights_new.txt
```
and
```
python3 flight_optimization.py generated_flights_new.txt
```

You can view output of the information (`profitable_flights.txt`) via an editor or executing in the terminal,

```
cat profitable_flights.txt
```
or
```
less profitable_flights.txt
```

***Run Visualization of Programs***

With the usage of `airport_sim.py`, these output files from all three previous programs (`profitable_flights.txt`, `generated_flights_new.txt`, `sorted_flights_new.txt`) can be visualized in an animation.
Run the possible commands for desired output:

```
python3 airport_sim.py profitable_flights.txt
```

```
python3 airport_sim.py generated_flights_new.txt
```

```
python3 airport_sim.py sorted_flights_new.txt
```

To close animation, abort the task in terminal with Ctrl c.

**Analysis of All Programs**

After running all steps before, we can produce a bar graph that analyzes across all three output files on the variables of profitability (total net profit), total passenger miles (Traveled distance/Demand), and total passengers.
Execute the following command:

```
python3 flight_graphs.py
```

To close animation, abort the task in terminal with Ctrl c.

** FINSHED **



