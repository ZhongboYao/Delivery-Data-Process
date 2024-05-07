import cluster
import process
import folium
import tools
from folium import LayerControl
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from pyproj import Proj, transform
import math
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import minimize_scalar

def latlon_to_utm(loc):
    x, y = transform(proj_latlon, proj_utm, loc[1], loc[0]) # [long, lat]
    return x, y

def in_cirlce(point, center, radius):
    return np.linalg.norm(np.array(point) - np.array(center)) <= radius

def estimate_intersection_area(t, center1, center2, center3, max_radius, trials=500000):
    d1 = speed_start_sec * t
    d2 = speed_walking * (t1 - t)
    d3 = speed_end_sec * (t2 - t1 + t)

    xs = [center1[0], center2[0], center3[0]]
    ys = [center1[1], center2[1], center3[1]]
    min_x, max_x = min(xs) - max_radius, max(xs) + max_radius
    min_y, max_y = min(ys) - max_radius, max(ys) + max_radius

    points = np.random.uniform((min_x, min_y), (max_x, max_y), (trials, 2))
    count = sum(in_cirlce(p, center1, d1) and in_cirlce(p, center2, d2) and in_cirlce(p, center3, d3) for p in points)
    
    return -count

stops_csv = 'Datasets/Batch1/POD1.csv'
routes_csv = 'Datasets/Batch1/GPS1_W904.csv'

delivery_data = process.GroupedDataset(stops_csv, routes_csv)
delivery_data.time_normalisation(delivery_data.dataset_routes, 'Tid')
delivery_data.time_normalisation(delivery_data.dataset_stops, 'DeliveredAt')
delivery_data.routes_organise(['Name', 'date']) 
delivery_data.stops_organise(['Ruttnamn', 'date'])

examine_vehicles_names = ['W904']

filtered_stops, stops_dates = cluster.stops_filter(delivery_data, examine_vehicles_names, 2)
corresponding_routes = cluster.routes_filter(delivery_data, stops_dates, examine_vehicles_names)
cluster.find_nearest_trips(filtered_stops, corresponding_routes)

stop = list(delivery_data.stops['POD-W904-2023-08-10'])[5]
trip_example = stop.nearest_trip
start = trip_example.start
end = trip_example.end

speed_start_sec = start.speed * 1000 / 3600
speed_end_sec = end.speed * 1000 / 3600
speed_walking = 1.42

t1 = (stop.time - start.time).total_seconds()
t2 = (end.time - stop.time).total_seconds()

proj_utm = Proj(proj='utm', zone=33, ellps='WGS84', preserve_units=False)
proj_latlon = Proj(proj='latlong', datum='WGS84')

loc_start = latlon_to_utm(start.loc)
loc_stop = latlon_to_utm(stop.loc)
loc_end = latlon_to_utm(end.loc)

t_bounds = (min(0, t1-t2), t1)
max_radius = max(t1 * speed_start_sec, t2 * speed_end_sec, t1 * speed_walking)
result = minimize_scalar(estimate_intersection_area, bounds=t_bounds, args=(loc_start, loc_stop, loc_end, max_radius))

optimal_t = result.x

for t in [optimal_t]:
# for t in np.arange(min(0, t1-t2), t1):
    d1 = speed_start_sec * t
    d2 = speed_walking * (t1 - t)
    d3 = speed_end_sec * (t2 - t1 + t)

    # def objective_function(p, p1, p2, p3, d1, d2, d3):
    #     x, y = p
    #     return ((x - p1[0])**2 + (y - p1[1])**2 - d1**2)**2 + \
    #         ((x - p2[0])**2 + (y - p2[1])**2 - d2**2)**2 + \
    #         ((x - p3[0])**2 + (y - p3[1])**2 - d3**2)**2

    # def constraint_circle(p, center, radius):
    #     x, y = p
    #     return radius - np.hypot(x - center[0], y - center[1])

    # # Circle centers and radii
    # p1 = loc_start
    # p2 =  loc_stop
    # p3 = loc_end

    # # Constraints
    # constraints = [
    #     {'type': 'ineq', 'fun': constraint_circle, 'args': (p1, d1)},
    #     {'type': 'ineq', 'fun': constraint_circle, 'args': (p2, d2)},
    #     {'type': 'ineq', 'fun': constraint_circle, 'args': (p3, d3)}
    # ]

    # # Initial guess
    # initial_guess = [(p1[0] + p2[0] + p3[0]) / 3, (p1[1] + p2[1] + p3[1]) / 3]

    # # Run optimization
    # result = minimize(objective_function, initial_guess, args=(p1, p2, p3, d1, d2, d3),
    #                 method='SLSQP', constraints=constraints)

    # if result.success:
    #     optimized_location = result.x
    #     print("Optimized Location:", optimized_location)

    #     # Visualization code:
    fig, ax = plt.subplots()

    # Plotting circles
    circle1 = plt.Circle(loc_start, d1, color='green', fill=False, linewidth=2, label='Start Travel')
    circle2 = plt.Circle(loc_stop, d2, color='orange', fill=False, linewidth=2, label='Stop Travel')
    circle3 = plt.Circle(loc_end, d3, color='red', fill=False, linewidth=2, label='End Travel')

    ax.add_artist(circle1)
    ax.add_artist(circle2)
    ax.add_artist(circle3)

    # Plotting the estimated location
    # plt.plot(optimized_location[0], optimized_location[1], 'yo', markersize=5, label='Estimated Location')

    # Additional plot settings
    plt.scatter(loc_start[0], loc_start[1], c='green', label='Start')
    plt.scatter(loc_stop[0], loc_stop[1], c='orange', label='Stop')
    plt.scatter(loc_end[0], loc_end[1], c='red', label='End')
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('Trilateration using Least Squares')
    plt.legend()
    plt.axis('equal')

    # Set limits for better visibility
    plt.xlim(min(loc_start[0], loc_stop[0], loc_end[0]) - 10, max(loc_start[0], loc_stop[0], loc_end[0]) + 10)
    plt.ylim(min(loc_start[1], loc_stop[1], loc_end[1]) - 10, max(loc_start[1], loc_stop[1], loc_end[1]) + 10)

    plt.grid(True)

    print(t1, t2, speed_start_sec, speed_end_sec, d1, d2, d3)
    # plt.savefig(f'Trilateration/{t}.png')
    plt.show()