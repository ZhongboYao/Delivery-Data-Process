import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from pyproj import Proj, transform

# Define the projection: UTM zone 33N for example (choose the zone that fits your region)
# For a more general approach, you can calculate the UTM zone based on longitude
proj_utm = Proj(proj='utm', zone=33, ellps='WGS84', preserve_units=False)

# Define WGS 84 Latitude and Longitude projection
proj_latlon = Proj(proj='latlong', datum='WGS84')

def latlon_to_utm(lat, lon):
    """Convert latitude and longitude to UTM coordinates."""
    x, y = transform(proj_latlon, proj_utm, lon, lat)
    return x, y

# Example GPS coordinates
gps_p1 = (lat1, lon1)
gps_p2 = (lat2, lon2)
gps_p3 = (lat3, lon3)

# Convert GPS coordinates to UTM
p1 = latlon_to_utm(gps_p1[0], gps_p1[1])
p2 = latlon_to_utm(gps_p2[0], gps_p2[1])
p3 = latlon_to_utm(gps_p3[0], gps_p3[1])


def trilateration_least_squares(p1, d1, p2, d2, p3, d3):
    """
    Solve trilateration problem using least squares to handle overlapping circles.
    :param p1, p2, p3: Coordinates of the points (x1, y1), (x2, y2), (x3, y3)
    :param d1, d2, d3: Distances to the target from p1, p2, p3
    :return: (x, y) coordinates of the target
    """
    def residuals(p):
        x, y = p
        return [(x - p1[0])**2 + (y - p1[1])**2 - d1**2,
                (x - p2[0])**2 + (y - p2[1])**2 - d2**2,
                (x - p3[0])**2 + (y - p3[1])**2 - d3**2]

    initial_guess = [(p1[0] + p2[0] + p3[0]) / 3, (p1[1] + p2[1] + p3[1]) / 3]
    result = least_squares(residuals, initial_guess)
    return result.x

# Example usage:
p1 = (0, 0)
d1 = 5
p2 = (4, 0)
d2 = 3
p3 = (2, 4)
d3 = 2.5

location = trilateration_least_squares(p1, d1, p2, d2, p3, d3)

# Visualization code:
fig, ax = plt.subplots()

# Plotting circles
circle1 = plt.Circle(p1, d1, color='r', fill=False, linewidth=2, label='Circle 1')
circle2 = plt.Circle(p2, d2, color='g', fill=False, linewidth=2, label='Circle 2')
circle3 = plt.Circle(p3, d3, color='b', fill=False, linewidth=2, label='Circle 3')

ax.add_artist(circle1)
ax.add_artist(circle2)
ax.add_artist(circle3)

# Plotting the estimated location
plt.plot(location[0], location[1], 'yo', markersize=5, label='Estimated Location')

# Additional plot settings
plt.scatter([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], c='black', label='Known Points')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.title('Trilateration using Least Squares')
plt.legend()
plt.axis('equal')

# Set limits for better visibility
plt.xlim(min(p1[0], p2[0], p3[0]) - 10, max(p1[0], p2[0], p3[0]) + 10)
plt.ylim(min(p1[1], p2[1], p3[1]) - 10, max(p1[1], p2[1], p3[1]) + 10)

plt.grid(True)
plt.show()
