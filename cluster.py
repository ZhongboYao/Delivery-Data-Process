from process import GroupedDataset
from geopy.distance import geodesic
import folium
from folium import LayerControl
from folium import FeatureGroup
from instances import Trip
from datetime import timedelta
import tools
from typing import Tuple

def stops_filter(data:GroupedDataset, filter_names:list, time_shift:int) -> Tuple[dict, dict]:
    filtered_stops = {}
    stops_dates = {}
    
    for (key_stops, stops) in data.stops.items():
        stops_name = key_stops.split('-')[1]
        stops_date = stops[0].time.date().isoformat()
        stops_dates[stops_date] = 1

        if stops_name in filter_names:
            for stop in stops:
                stop.time = stop.time + timedelta(hours=time_shift)
                if (stops_name, stops_date) not in filtered_stops:
                    filtered_stops[(stops_name, stops_date)] = [stop]
                else:
                    filtered_stops[(stops_name, stops_date)].append(stop)

    return filtered_stops, stops_dates

def routes_filter(data:GroupedDataset, stops_dates:dict, filter_names:list) -> dict:
    filtered_routes = {}

    for (key_route, route) in data.routes.items():
        route_name = key_route.split('-')[1]
        route_date = route.trips[0].start.time.date().isoformat()
        if route_name in filter_names and route_date in stops_dates :
            filtered_routes[(route_name, route_date)] = route

    return filtered_routes

def nearest_trip_match(stops:list, points:list):
    i = 0
    j = 1
    while i < len(stops) and j < len(points):
        stop = stops[i]
        if stop.time >= points[j-1].time and stop.time <= points[j].time:
            stop.nearest_trip = Trip(points[j-1], points[j])
            for point in [points[j-1], points[j]]:
                if point.speed <= 1:
                    stop.parked_points.append(point)
            i += 1
        else:
            j += 1

def find_nearest_trips(filtered_stops:dict, filtered_routes:dict):
    for (stop_key, stops) in filtered_stops.items():
        stop_name = stop_key[0]
        stop_date = stop_key[1]
        if (stop_name, stop_date) in filtered_routes:
            selected_route = filtered_routes[(stop_name, stop_date)]
            nearest_trip_match(stops, selected_route.points)

stops_csv = 'Datasets/Batch1/POD1.csv'
routes_csv = 'Datasets/Batch1/GPS1_W904.csv'

delivery_data = GroupedDataset(stops_csv, routes_csv)
delivery_data.time_normalisation(delivery_data.dataset_routes, 'Tid')
delivery_data.time_normalisation(delivery_data.dataset_stops, 'DeliveredAt')
delivery_data.routes_organise(['Name', 'date']) 
delivery_data.stops_organise(['Ruttnamn', 'date'])

examine_vehicles_names = ['W904']

filtered_stops, stops_dates = stops_filter(delivery_data, examine_vehicles_names, 2)
corresponding_routes = routes_filter(delivery_data, stops_dates, examine_vehicles_names)
find_nearest_trips(filtered_stops, corresponding_routes)

map = folium.Map(location=[59.3293, 18.0686], zoom_start=12)
tools.nearest_trip_plot(filtered_stops, map)

LayerControl().add_to(map)
map.save('Maps/batch1_nearest_points.html')



            
            
        


