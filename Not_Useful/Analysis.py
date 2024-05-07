import matplotlib.pyplot as plt
import numpy as np

def bar_plot(x, y, xlabel, ylabel, title, savepath, avg=None, avglabel=None, sort=True):
    fig, ax = plt.subplots(figsize=(13, 12))

    if x == None:
        sorted_indices = np.argsort(y)
        y = np.array(y)[sorted_indices]
        x = [f"{i+1}" for i in range(len(y))]
        ax.set_xticklabels([])

    if sort:
        paired = zip(x, y)
        sorted_pairs = sorted(paired, key=lambda pair: pair[1], reverse=True)
        x, y = zip(*sorted_pairs)

    ax.bar(x, y, color='orange', alpha=0.7)
    if avg is not None:
        ax.axhline(y=avg, color='r', linestyle='-', linewidth=1, label=avglabel)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.tick_params(labelrotation=45) 
    ax.grid(axis='y', alpha=0.75)
    ax.legend()
    fig.savefig(savepath)

def hist_plot(x, bin_width, xlabel, ylabel, title, savepath):
    fig, ax = plt.subplots(figsize=(13, 12))
    min_edge = min(x)
    max_edge = max(x) + bin_width  
    bins = np.arange(int(min_edge), int(max_edge) + bin_width, bin_width)  
    ax.hist(x, bins=bins, color='orange', alpha=0.7, rwidth=0.85)
    ax.grid(axis='y', alpha=0.75)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    bin_labels = [f"{bins[i]:.1f}-{bins[i+1]:.1f}" for i in range(len(bins)-1)]
    ax.set_xticks(bins[:-1] + bin_width/2)
    ax.set_xticklabels(bin_labels, rotation=45, ha="right")
    ax.set_title(title)
    fig.savefig(savepath)

def plot_data(routes):
    routes_distance = []
    routes_name = []
    routes_stops_num = []
    routes_time = []
    routes_speed = []

    trips_speed = []
    trips_distance = []
    trips_time = []

    for route in routes.values():
        routes_name.append(route.name)
        routes_distance.append(route.total_distance)
        routes_stops_num.append(route.num_stops)
        routes_time.append(route.total_time.total_seconds()/3600)
        routes_speed.append(route.avg_speed)
        for trip in route.trips:
            trips_speed.append(trip.speed)
            trips_distance.append(trip.distance)
            trips_time.append(trip.travel_time.total_seconds()/3600)

    avg_stops_num = sum(routes_stops_num)/len(routes)
    avg_distance = sum(routes_distance)/len(routes)
    avg_time = sum(routes_time)/len(routes)
    avg_speed = sum(routes_speed)/len(routes)

    avg_trip_distance = sum(trips_distance)/len(trips_distance)
    avg_trip_time = sum(trips_time)/len(trips_time)
    avg_trip_speed = sum(trips_speed)/len(trips_speed)

    bar_plot(routes_name, routes_distance, 'Routes Names', 'Distance (Km)', 'Bar Chart of Routes Distances', 'Data Statistics/routes_distance_bar', avg_distance, f'Average Distance: {avg_distance:.2f} Km')
    hist_plot(routes_distance, 7, 'Distance (Km)', 'Frequency', 'Histogram of Route Distances', 'Data Statistics/routes_distance_hist')
    bar_plot(routes_name, routes_stops_num, 'Routes Names', 'Number of Stops', 'Bar Chart of the Number of Stops', 'Data Statistics/routes_stopsNum_bar', avg_stops_num, f'The Average Number of Stops: {avg_stops_num:.2f}')
    hist_plot(routes_stops_num, 3, 'The Number of Stops', 'Frequency', 'Histogram of the Number of Stops', 'Data Statistics/routes_stopsNum_hist')
    bar_plot(routes_name, routes_time, 'Routes Names', 'Time Spent (Hours)', 'Bar Chart of Time Spent', 'Data Statistics/routes_time_bar', avg_time, f'Average Travel Time: {avg_time:.2f} (Hours)')
    hist_plot(routes_time, 0.5, 'Time Spent (Hours)', 'Frequency', 'Histogram of Travel Time', 'Data Statistics/routes_time_hist')
    bar_plot(routes_name, routes_speed, 'Routes Names', 'Speed (Km/Hr)', 'Bar Chart of Speed', 'Data Statistics/routes_speed_bar', avg_speed, f'Average Speed: {avg_speed:.2f} (Km/Hr)')
    hist_plot(routes_speed, 1.5, 'Speed (Km/Hr)', 'Frequency', 'Histogram of Speed', 'Data Statistics/routes_speed_hist')

    bar_plot(None, trips_distance, 'Nr.', 'Distance (Km)', 'Bar Chart of Trips Distances', 'Data Statistics/trips_distance_bar', avg_trip_distance, f'Average Distance: {avg_trip_distance:.2f} Km')
    hist_plot(trips_distance, 0.5, 'Distance (Km)', 'Frequency', 'Histogram of Trip Distances', 'Data Statistics/trips_distance_hist')
    bar_plot(None, trips_time, 'Nr.', 'Time Spent (Hours)', 'Bar Chart of Time Spent', 'Data Statistics/trips_time_bar', avg_trip_time, f'Average Travel Time: {avg_trip_time:.2f} (Hours)')
    hist_plot(trips_time, 0.1, 'Time Spent (Hours)', 'Frequency', 'Histogram of Travel Time', 'Data Statistics/trips_time_hist')
    bar_plot(None, trips_speed, 'Nr.', 'Speed (Km/Hr)', 'Bar Chart of Speed', 'Data Statistics/trips_speed_bar', avg_trip_speed, f'Average Speed: {avg_speed:.2f} (Km/Hr)')
    hist_plot(trips_speed, 1, 'Speed (Km/Hr)', 'Frequency', 'Histogram of Speed', 'Data Statistics/trips_speed_hist')

def correlation_CityTime(routes, savepath):
    stops_city = []
    trip_time = []
    for route in routes.values():
        for trip in route.trips:
            stops_city.append(trip.end.city)
            trip_time.append(trip.travel_time.total_seconds()/60)

    paired = zip(stops_city, trip_time)
    sorted_pairs = sorted(paired, key=lambda pair: pair[1], reverse=True)
    x, y = zip(*sorted_pairs)

    fig, ax = plt.subplots(figsize=(14, 13))
    ax.scatter(x, y, s=2, color='orange')
    ax.set_xlabel('Cities')
    ax.set_ylabel('Time Spent Each Stop (Minutes)')
    ax.set_title('Distribution of Time Spent on Each Stop among Cities')
    ax.tick_params(labelrotation=45) 
    fig.savefig(savepath)

# correlation_CityTime(routes, 'Data Statistics/correlation')
# plot_data(routes)