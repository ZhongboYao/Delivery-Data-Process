import pandas as pd
import folium
import tools
import instances

class GroupedDataset:
    def __init__(self, dataset_stops_loc:str, dataset_routes_loc:str):
        """
        Arguments:
        dataset_stops_loc, dataset_routes_loc: The location of the dataset to be visualised.
        """
        self.dataset_routes = pd.read_csv(dataset_routes_loc).copy()
        self.dataset_stops = pd.read_csv(dataset_stops_loc).copy()
        self.map = folium.Map(location=[59.3293, 18.0686], zoom_start=12)
        self.routes = None
        self.stops = None

    def time_normalisation(self, dataset:pd, col_name:str):
        """
        Normalise the time feature of the dataset to standard time values and add a date feature to the dataset for grouping.

        Arguments:
        dataset: The dataset to be normalised.
        col_name: The name of the column in the dataset representing the time.
        """
        dataset['timevalue'] = pd.to_datetime(dataset[col_name], format='mixed', dayfirst=True) 
        dataset['date'] = dataset['timevalue'].dt.date

    def routes_organise(self, col_names:list):
        """
        Group the routes according to the routines' names and sort them according to the time.
        Then store the grouped and sorted ones into the self.routes.

        Arguments:
        col_names: A list containing features according to which the routes are grouped.
        """
        routes = {}
        grouped_dataset = tools.group_data(self.dataset_routes, col_names)
        for group_keys, data in grouped_dataset:
            data_sorted = data.sort_values(by='timevalue')
            route = instances.Route('GPS-' + f'{"-".join(map(str, group_keys))}', data_sorted)
            routes[route.name] = route
        self.routes = routes

    def stops_organise(self, col_names:list):
        """
        Group the destinations according to the stops' names and col_names.
        Then store the grouped and sorted ones into the self.destinations.

        Arguments:
        col_names: A list containing features according to which the routes are grouped.
        """
        stops = {}
        grouped_dataset = tools.group_data(self.dataset_stops, col_names)
        for group_keys, group in grouped_dataset:
            stops_sorted = group.sort_values(by='timevalue') # Sorting this helps find the nearest GPS points.
            for _, data in stops_sorted.iterrows():
                stop = instances.Stop(data)
                # To initialise the empty dictionary.
                if 'POD-' + f'{"-".join(map(str, group_keys))}' not in stops:
                    # Example key for stops in the dictionary: 'W904-2023-09-01'
                    stops['POD-' + f'{"-".join(map(str, group_keys))}'] = [stop]
                else:
                    stops['POD-' + f'{"-".join(map(str, group_keys))}'].append(stop)
        self.stops = stops