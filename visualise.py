from folium import LayerControl
import tools
from process import GroupedDataset

def visualisation(dataset:GroupedDataset, loc:str):
    """
    Visualise the data points and routines on the Stockholm's map.

    Arguments: 
    dataset: The dataset processed by Group_dataset.
    loc: The location to save the plotted map.
    """
    tools.routes_plot(dataset.map, dataset.routes)
    tools.stops_plot(dataset.map, dataset.stops)
    LayerControl().add_to(dataset.map)
    dataset.map.save(loc)

stops_csv = 'Datasets/Batch3/POD3.csv'
routes_csv = 'Datasets/Batch3/GPS3.csv'

tools.xlsx_to_csv(excel_file_path='Datasets/Batch3/POD3.xlsx', csv_file_path=stops_csv)
tools.xlsx_to_csv(excel_file_path='Datasets/Batch3/GPS3.xlsx', csv_file_path=routes_csv)

dataframe = GroupedDataset(stops_csv, routes_csv)
dataframe.time_normalisation(dataframe.dataset_stops, 'DeliveredAt')
dataframe.time_normalisation(dataframe.dataset_routes, 'Tid')
dataframe.routes_organise(['Name', 'date']) 
dataframe.stops_organise(['Ruttnamn', 'date'])
visualisation(dataframe, 'Maps/batch3.html')
