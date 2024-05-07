import hashlib
from folium import FeatureGroup
import osmnx as ox
import folium
import pandas as pd
import branca.colormap as cm
from folium import Popup
from folium.plugins import PolyLineTextPath


def xlsx_to_csv(excel_file_path:str, csv_file_path:str):
    """
    Transfer a .xlsx file into a .csv file.

    Parameters:
    excel_file_path, csv_file_path: As the names indicated.
    """
    df = pd.read_excel(excel_file_path)
    df.to_csv(csv_file_path, index=False)

def get_color(input_string:str) -> str:
        """
        Generates a color for a route given its name.

        Parameters:
        input_string: The name of the route.
        
        Returns:
        The color of the designated route.
        """
        hash_obj = hashlib.sha256(input_string.encode())
        return '#' + hash_obj.hexdigest()[:6]

def reverse_colormap(original_colormap:cm) -> cm:
    """
    Reverse the sequence of colors of a colormap, so that the colors change from bright to dark.

    Arguments:
    original_colormap: The used colormap in its original sequence.

    Returns:
    Reversed colormap.
    """
    colors = original_colormap.colors
    reversed_colors = list(reversed(colors))
    
    reversed_colormap = cm.LinearColormap(
        colors=reversed_colors,
        vmin=original_colormap.vmin,
        vmax=original_colormap.vmax
    )

    return reversed_colormap

def group_data(dataset:pd, col_names:list) -> pd:
    """
    Group the dataset in the given file according to the col names loaded in the list called col_names, and return the grouped dataset.

    Arguments:
    dataset: The dataset read by pandas to be grouped.
    col_names: The list of col names accoridng to which the dataset is grouped.
    """
    return dataset.groupby(col_names)

def routes_plot(map:folium, routes:dict, filter:list=None, G:ox=None):
    """
    Illustrate information points, trips and routes in the map.
    The result is illustrated in a .html map.

    Parameters:
    map: The map on which data is visualised.
    routes: A dictionary of all the routes need to be visualised.
    loc: The location to store the map.
    filter: A list of point types to be illustrated on the map.
    G: The traffic graph.
    """
    
    for name, route in routes.items():
        route_color = route.color
        feature_group = FeatureGroup(name=name, show=False)
        time_steps = []
        ref = route.points[0].time

        for point in route.points:
            if filter == None or point.type in filter:
                folium.CircleMarker(
                    location=point.loc,
                    radius=5,
                    color=point.color,
                    fill=True,
                    fill_color=point.color,
                    fill_opacity=2,
                    popup=folium.Popup(f"Time: {point.time} Location: {point.loc} Rutt: {name} Type: {point.type}", parse_html=True)
                ).add_to(feature_group)
            time_steps.append((point.time - ref).total_seconds())
        
        colormap = cm.linear.inferno.scale(0, route.total_distance)
        reversed_colormap = reverse_colormap(colormap)
        
        total_distances = [5] # Used for adjusting the color for the start point of the route.
        for (i, trip) in enumerate(route.trips):
            total_distances.append(total_distances[i]+(trip.distance)/2.2)
            if trip.exact_path != None:
                latlngs = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in trip.exact_path]
                folium.PolyLine(latlngs, color=route_color, weight=4, opacity=1).add_to(feature_group)
            else:
                folium.ColorLine([trip.start.loc, trip.end.loc], colors=[total_distances[i], total_distances[i+1]], colormap=reversed_colormap, weight=4, opacity=1).add_to(feature_group)
                
        feature_group.add_to(map)

def stops_plot(map:folium, stops:dict, filter:list=None):
    """
    Illustrate stops in the map.
    The result is illustrated in a .html map.

    Parameters:
    map: The map on which data is visualised.
    stops: A dictionary of all the stops need to be visualised.
    filter: A list of point types to be illustrated on the map.
    """

    for (name, stop_list) in stops.items():
        feature_group = FeatureGroup(name=name, show=False)
        for stop in stop_list:
            if filter == None or stop.type in filter:
                folium.CircleMarker(
                    location=stop.loc,
                    radius=10,
                    color=stop.color,
                    fill=True,
                    fill_color=stop.color,
                    fill_opacity=2,
                    popup=folium.Popup(f"Time: {stop.time} Location: {stop.loc} Rutt: {name} Type: {stop.type}", parse_html=True)
                ).add_to(feature_group)
                
        feature_group.add_to(map)

def nearest_trip_plot(filtered_stops:dict, map:map):
    for (stops_key, stops) in filtered_stops.items():
        flag = 0
        stops_name = stops_key[0]
        stops_date = stops_key[1]
        name = f'{stops_name}-{stops_date}'
        feature_group = FeatureGroup(name=name, show=False)

        for stop in stops:
            if stop.nearest_trip != None:
                flag = 1

                # Illustration of the delivery stop.
                folium.CircleMarker(
                    location=stop.loc,
                    radius=8,
                    color=stop.color,
                    fill=True,
                    fill_color=stop.color,
                    fill_opacity=2,
                    popup=folium.Popup(f"Time: {stop.time} Location: {stop.loc} Rutt: {None} Type: {stop.type}", parse_html=True)
                ).add_to(feature_group)
                
                # Illustration of the nearest trip.
                points = [stop.nearest_trip.start, stop.nearest_trip.end]
                for point in points:
                    folium.CircleMarker(
                        location=point.loc,
                        radius=5,
                        color=point.color,
                        fill=True,
                        fill_color=point.color,
                        fill_opacity=2,
                        popup=folium.Popup(f"Time: {point.time} Location: {point.loc} Rutt: {None} Type: {point.type} Speed: {point.speed}", parse_html=True)
                    ).add_to(feature_group)
                    line = folium.PolyLine([points[0].loc, points[1].loc], color='orange', weight=4, opacity=1).add_to(feature_group)
                    PolyLineTextPath(
                        line,
                        '\u25BA',  # Unicode character for an arrowhead (can also use other arrow symbols like '→' or '►')
                        repeat=True,
                        offset=6,
                        attributes={'fill': 'orange', 'font-weight': 'bold', 'font-size': '18'}
                    ).add_to(feature_group)

                # Illustration of the possible parking locations.
                for point in stop.parked_points:
                    line = folium.PolyLine([point.loc, stop.loc], color='blue', weight=4, opacity=1)
                    line.add_to(feature_group)
                    
                    PolyLineTextPath(
                        line,
                        '\u25BA',  # Unicode character for an arrowhead (can also use other arrow symbols like '→' or '►')
                        repeat=True,
                        offset=6,
                        attributes={'fill': 'blue', 'font-weight': 'bold', 'font-size': '18'}
                    ).add_to(feature_group)    
            
            if flag:
                feature_group.add_to(map)