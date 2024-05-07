import pandas as pd
from datetime import timedelta
import osmnx as ox
from geopy.distance import geodesic
from tools import get_color

class Stop:
    """
    Each delivery destionation.
    """
    def __init__(self, record:pd):
        """
        Parameters:
        record: A line of data read by Pandas.
        """
        self.time = record['timevalue'] 
        self.type = 'Destination'
        self.color = 'red'
        self.loc = [record['ConfirmedCoordinates.Latitude'], record['ConfirmedCoordinates.Longitude']]
        self.city = record['Address.City']
        self.nearest_trip = None
        self.parked_points = []

class Info_point:
    """
    Each information state point uploaded in the GPS information file.
    """
    def __init__(self, record:pd):
        """
        Parameters:
        record: A line of data read by Pandas.
        """
        self.time = record['timevalue'] 
        self.type = record['Händelse']
        self.color = get_color(self.type)
        self.loc = [record['Lat'], record['Long']]
        self.speed = record['Hastighet']
        
class Trip:
    """
    Route between two stops.
    """
    def __init__(self, start:Info_point, end:Info_point):
        """
        Parameters:
        start, end: The start and end points.
        """
        self.start = start
        self.end = end
        self.distance = None
        self.travel_time = None
        self.speed = None
        self.exact_path = None
        self.get_properties()

    def get_properties(self):
        self.travel_time = self.end.time - self.start.time # In pandas time values format.
        self.distance = geodesic(self.start.loc, self.end.loc).meters/1000

        if self.travel_time.total_seconds() == 0:
            self.speed = 0
        else:
            self.speed = self.distance / (self.travel_time.total_seconds()/3600)

    def get_exact_path(self, G) -> ox.graph:
        """
        Given the start and the end location, this function matches each route into exact routes.

        Arguments:
        G: The graph of the city containing road information and coordinates.

        Returns:
        The extended graph G.
        """
        existing_nodes = set(G.nodes)

        for stop in (self.start, self.end):
            if self.distance != 0:
                dist = self.distance
            else:
                dist = 100

            try:
                G_sub = ox.graph_from_point(stop.loc, dist=dist, network_type='drive_service', simplify=False, truncate_by_edge=True)
                for node, data in G_sub.nodes(data=True):
                    if node not in existing_nodes:
                        G.add_node(node, **data)
                        existing_nodes.add(node)
                    for u, v, key, data in G_sub.edges(keys=True, data=True):
                        if not G.has_edge(u, v, key):
                            G.add_edge(u, v, key=key, **data)
            except:
                pass

        start_node = ox.distance.nearest_nodes(G, X=self.start.loc[1], Y=self.start.loc[0])
        stop_node = ox.distance.nearest_nodes(G, X=self.end.loc[1], Y=self.end.loc[0])
        shortest_path = ox.routing.shortest_path(G, start_node, stop_node, weight='length')
        self.exact_path = shortest_path

        return G

class Route:
    """
    Contains all the trips travelled by a single vehicle.
    """
    def __init__(self, name:str, data:pd):
        """
        Parameters:
        name: The name of this route.
        data: All the saved information of this route, read using Pandas. 
        """
        self.name = name   
        self.color = get_color(self.name)
        self.data = data
        self.points = self.points_extraction() # [Info_point1, Info_point2 ...] sorted according to arrival times.
        self.trips = self.trips_creation() # [Trip1, Trip2, ...] sorted according to arrival times.
        self.total_distance = None
        self.total_time = None 
        self.avg_speed = None
        self.get_properties()

    def points_extraction(self):
        """
        Reads and creates all the information points in a route and stores them into a list.

        Parameters:
        data: Data of a route, read by Pandas.

        Returns: 
        A list of points
        """
        points = []
        for _, record in self.data.iterrows():
            points.append(Info_point(record))
        return points
    
    def trips_creation(self) -> list:
        """
        Creates trips of a route and stores it into a list.

        Returns:
        A list of trips.
        """
        trips = []
        if len(self.points) >= 2:
            for i in range(len(self.points) - 1):
                trip = Trip(self.points[i], self.points[i+1])
                trips.append(trip)
        return trips
    
    def get_properties(self):
        """
        Calculate the total distance, total time consumed and average speed of this route.
        """
        total_distance = 0
        total_time = timedelta()

        for trip in self.trips:
            total_distance += trip.distance
            total_time = total_time + trip.travel_time

        if total_time.total_seconds() == 0:
            avg_speed = 0
        else:
            avg_speed = total_distance / (total_time.total_seconds()/3600)
        
        self.total_distance = total_distance
        self.total_time = total_time 
        self.avg_speed = avg_speed
