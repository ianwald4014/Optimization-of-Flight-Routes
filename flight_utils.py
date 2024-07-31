import pprint
from math import radians, sin, cos, sqrt, atan2
import itertools

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

def rearrange_cities_for_shortest_path(city_list):
    """Takes a list of cities, and rearranges them so that the path
    between them is shortest.  The first city has to be the same, the
    others are reordered to make the total distance the least."""
    if len(city_list) == 2:
        return city_list
    c0 = city_list[0]
    # make all possible rearranged flight orders for the other cities
    print('ORIG:', city_list)
    permuted_other_cities = list(itertools.permutations(city_list[1:]))
    cities_and_length_list = []
    for candidate_path in permuted_other_cities:
        total_candidate_path = [c0] + list(candidate_path)
        pathlength = calc_distance_new(total_candidate_path)
        cities_and_length_list.append((total_candidate_path, pathlength))
    # now that we have the list of all candidate paths, let's sort it
    # by the length, which is the second bit of the pair
    cities_and_length_list.sort(key=lambda the_pair: the_pair[1])
    # print('SORTED:', cities_and_length_list)
    optimal_city_list = cities_and_length_list[0][0]
    print('OPTIMAL:', optimal_city_list)
    return optimal_city_list
        
def flight_path2city_list(flight_path_str):
    """Takes a string with a flight path (example: "DEN, ABQ, LAX, JFK")
    and returns the list of cities (in this case ["DEN", "ABQ", "LAX",
    "JFK"])."""
    city_list = flight_path_str.split(',')
    city_list = [city.strip() for city in city_list if city.strip() != 'None']
    return city_list

def calc_distance_new(city_list):
    """Takes an ordered city list and calculates the total distance
    traveled."""
    # algorithm: distance between pairs of cities in order
    total_distance = 0
    for i in range(len(city_list) - 1):
        total_distance += city2city_distance(city_list[i], city_list[i+1])
    return total_distance

def city2city_distance(c1, c2):
    """Take two airport codes and return the distance between them."""
    (lat1, lon1) = (airports[c1]['lat'], airports[c1]['lon'])
    (lat2, lon2) = (airports[c2]['lat'], airports[c2]['lon'])
    return haversine_distance_nm(lat1, lon1, lat2, lon2)

def haversine_distance_nm(lat1, lon1, lat2, lon2): # AOI
    """Calculate distance in nautical miles using the haversine formula."""
    R = 3440.065  # Radius of Earth in nautical miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance_nm = R * c
    return distance_nm


def calculate_flight_time(lon1, lat1, lon2, lat2):
    """Calculate flight time and operational cost."""
    if None in [lat1, lon1, lat2, lon2]:
        return 0, 0  # Handle invalid coordinates
    distance_nm = haversine_distance_nm(lat1, lon1, lat2, lon2)
    speed_knots = 485  # Average speed of a Boeing 737 MAX in knots
    flight_time = distance_nm / speed_knots
    operational_cost = 5757 * flight_time
    return flight_time, operational_cost

def load_flights_newstyle(fname):
    """Loads flights from a flight path file, and returns a dictionary
    with all the info."""
    all_flights = []
    with open(fname, 'r') as fp:
        # first break it into records separated by
        # __FLIGHT_RECORD_SEPARATOR__
        all_txt = fp.read()
        record_strings = all_txt.split('__FLIGHT_RECORD_SEPARATOR__')
        for record in record_strings:
            record_dict = parse_record(record)
            # now append to the overall list
            all_flights.append(record_dict)
            # # special: use the flight_number as the key into the
            # # overall dictionary of *all* flights
            # all_flights[record_dict['flight_number']] = record_dict
    return all_flights


def parse_record(record_str):
    """record_str has a list of lines with keyword-value pairs; make a
    dictionary with those keyword/values."""
    result = {}
    record_str = record_str.strip()
    for line in record_str.split('\n'):
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        # make sure keys don't appear twice
        assert(not key in result)
        result[key] = value
    return result


def append_newstyle_route(fp, newstyle_route):
    """Takes a file object already open for writing and appends a route to
    it."""
    # print('ABOUT:', newstyle_route)
    for key in newstyle_route:
        # print(key, newstyle_route[key])
        fp.write(f"{key}: {newstyle_route[key]}\n")


def write_flights_newstyle(fname, newstyle_all_routes):
    """Takes a list of routes (newstyle) a simple file with record
    separators and each record having "key: value" lines."""
    with open(fname, 'w') as fp:
        for order_no, route in enumerate(newstyle_all_routes):
            # pprint.pprint(route)
            # print('WRITING_NEWSTYLE:', route['flight_number'])
            append_newstyle_route(fp, route)
            # don't put record separator for the last one
            if order_no != len(newstyle_all_routes) - 1:
                fp.write('__FLIGHT_RECORD_SEPARATOR__\n')
    print('# wrote newstyle routes to file', fname)


def write_flights_oldstyle2newstyle(fname, oldstyle_all_routes):
    """Takes the rather elaborate routes dictionary and writes a simple
    file with just the essential entries."""
    with open(fname, 'w') as fp:
        for order_no, oldstyle_route in enumerate(oldstyle_all_routes):
            print('ANOTHER_OLDSTYLE_WRITING:', oldstyle_route['Route'])
            newstyle_dict = {}
            newstyle_dict['flight_number'] = oldstyle_route['Route']
            newstyle_dict['origin'] = oldstyle_route['Origin']
            newstyle_dict['destination'] = oldstyle_route['Destination']
            newstyle_dict['passengers'] = oldstyle_route['Passengers']
            newstyle_dict['flight_path'] = (oldstyle_route['Origin']
                                            + ", " + oldstyle_route['Stop1']
                                            + ", " + oldstyle_route['Stop2']
                                            + ", " + oldstyle_route['Destination'])
            newstyle_dict['n_stops'] = oldstyle_route['Stops']
            append_newstyle_route(fp, newstyle_dict)
            # don't do it for the last one
            if order_no != len(oldstyle_all_routes) - 1:
                fp.write('__FLIGHT_RECORD_SEPARATOR__\n')
    print('# wrote newstyle routes to file', fname)



def convert_route_oldstyle2newstyle(oldstyle_route):
    """Takes the rather elaborate oldstyle route dictionary and returns a
    simpler newstyle one with just the necessary information:
    flight_number, origin, destination, passengers, flight_path, and
    n_stops.
    """
    print('OLDSTYLE_ROUTE2NEW:', oldstyle_route['Route'])
    newstyle_dict = {}
    newstyle_dict['flight_number'] = oldstyle_route['Route']
    newstyle_dict['origin'] = oldstyle_route['Origin']
    newstyle_dict['destination'] = oldstyle_route['Destination']
    newstyle_dict['passengers'] = oldstyle_route['Passengers']
    newstyle_dict['flight_path'] = (oldstyle_route['Origin']
                                    + ", " + oldstyle_route['Stop1']
                                    + ", " + oldstyle_route['Stop2']
                                    + ", " + oldstyle_route['Destination'])
    newstyle_dict['n_stops'] = oldstyle_route['Stops']
    return newstyle_dict
