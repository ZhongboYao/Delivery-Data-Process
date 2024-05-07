import csv
import googlemaps
from process import haversine
import osmnx as ox
from tqdm import tqdm
import pandas as pd
import networkx as nx

def address_retrieve(lat, lng):
    '''
    Address localization.
    Given latitude and longitude, returns the postcode and the corresponding address name.
    '''
    reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
    postcode = None
    full_address = None
    if reverse_geocode_result:
        for component in reverse_geocode_result[0]['address_components']:
            if 'postal_code' in component['types']:
                postcode = component['long_name']
                break 
        full_address = reverse_geocode_result[0].get('formatted_address')
    return postcode, full_address

def coordinate_retrieve(address):
    '''
    Returns latitude and longitude given the address name.
    '''
    geocode_result = gmaps.geocode(address)
    lat = 0
    lng = 0
    if geocode_result:
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
    return lat, lng

def morphology_attributes(center_point, radius=100):
    '''
    Get the averaged node degree, the number of sections, average node connectivity, edge connectivity and the density of the graph within that the range of the center point.
    Radius is in meters.
    '''
    G = ox.graph_from_point(center_point, dist=radius, network_type='drive_service', truncate_by_edge=True)
    G_undirected = G.to_undirected()
    node_degrees = dict(G_undirected.degree()) # It returns a dict containing the degrees of all the nodes within G.
    density = nx.density(G_undirected)
    intersection_num = len(node_degrees)
    average_nodeConnectivity = nx.average_node_connectivity(G_undirected)
    edgeConnectivity = nx.edge_connectivity(G_undirected)
    average_degree = sum(node_degrees.values()) / intersection_num
    ox.plot_graph(G)
    return intersection_num, average_degree, density, average_nodeConnectivity, edgeConnectivity

class Expansion:
    def address_match_check(self, csv_file_path, new_csv_file_path, name_correction=1):
        '''
        Expand the dataset with the address name and postcodes retrieved according to the provided 
        coordinate and whether they matche with the ones given in the dataset.
        '''
        address_match_counter = 0
        postcode_match_counter = 0
        counter = 0
        
        with open(csv_file_path, newline='') as csvfile, open(new_csv_file_path, 'w', newline='') as newfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(newfile)
            
            header = next(reader)
            header.extend(['Retrived Address', 'Address Match', 'Retrieved Postcode', 'Postcode Match'])
            writer.writerow(header)

            for row in reader:
                counter += 1

                address = row[0].split()[0]
                postcode = row[2][:3] + " " + row[2][3:]
                latitude = row[3]
                longitude = row[4]

                retrieved_postcode, retrieved_address = address_retrieve(latitude, longitude)
                if name_correction:
                    retrieved_address = retrieved_address.replace('ö', 'å')

                postcode_match = (postcode == retrieved_postcode)
                address_match = (address == retrieved_address.split()[0])

                row.extend([retrieved_address, address_match, retrieved_postcode, postcode_match])
                writer.writerow(row)

                if address_match == 1:
                    address_match_counter += 1
                if postcode_match == 1:
                    postcode_match_counter += 1

            print(f'Address Matching Rate {address_match_counter/counter}')
            print(f'Postcode Matching Rate {postcode_match_counter/counter}')

    def coordinate_difference_calculation(self, csv_file_path, new_csv_file_path, name_correction=1):
        '''
        Retrieve the GPS coordinate according to the given address name and calculate 
        the diffence bewteen the retrieved one and the given one.
        '''
        counter = 0
        total_distance_error = 0

        with open(csv_file_path, newline='') as csvfile, open(new_csv_file_path, 'w', newline='') as newfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(newfile)
            
            header = next(reader)
            header.extend(['Retrieved Lat', 'Retrieved Long', 'Distance Error (Meters)'])
            writer.writerow(header)

            for row in reader:
                counter += 1

                address = row[0]
                latitude = row[3]
                longitude = row[4]

                if name_correction == 1:
                    address = address.replace('å', 'ö')
                retrieved_lat, retrieved_long = coordinate_retrieve(address)

                distance_error = haversine([float(latitude), float(longitude)], [retrieved_lat, retrieved_long]) * 100
                total_distance_error += distance_error

                row.extend([retrieved_lat, retrieved_long, distance_error])
                writer.writerow(row)
            
            avg_distance_error = total_distance_error/counter

            print(f'Average Distance Error {avg_distance_error} (Meters)')

    def morphology(self, csv_file_path, new_csv_file_path):
        df = pd.read_csv(csv_file_path)
        num_rows = len(df) - 1

        with open(csv_file_path, newline='') as csvfile, open(new_csv_file_path, 'w', newline='') as newfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(newfile)
            
            header = next(reader)
            header.extend(['Nr. Intersections', 'Avg Node Degree', 'Density', 'Average Node Connectivity', 'Edge Connectivity'])
            writer.writerow(header)

            with tqdm(total = num_rows) as pbar:
                for row in reader:
                    pbar.update(1)
                    latitude = float(row[3])
                    longitude = float(row[4])
                    try:
                        intersection_num, degree, density, average_nodeConnectivity, edgeConnectivity = morphology_attributes((latitude, longitude))      
                    except Exception:
                        intersection_num, degree, density, average_nodeConnectivity, edgeConnectivity = ('!', '!', '!', '!', '!')
                        pass
                    row.extend([intersection_num, degree, density, average_nodeConnectivity, edgeConnectivity])
                    writer.writerow(row)

gmaps = googlemaps.Client(key='AIzaSyBFJyArj6F3I1w8MBG4uyBpRrpvAK2FyIA')
path0 = 'Data.csv'
path1 = 'Data1.csv'
path2 = 'Data2.csv'
path3 = 'Data3.csv'

processor = Expansion()
processor.address_match_check(path0, path1)
processor.coordinate_difference_calculation(path1, path2)
processor.morphology(path2, path3)