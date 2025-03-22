import geopandas as gpd
import numpy as np
from pulp import *


# Load the shapefile
gdf = gpd.read_file("land_parcels.shp")

# Basic info
#print(gdf.head())

print("\n\n-------------------------------INFO BELOW-------------------------------\n")
#print(gdf.info())

# Number of polygons
num_polygons = len(gdf)
print("NUMBER OF POLYGONS: {}".format(num_polygons))

carbon = gdf["carbon_sto"]

#print(gdf)
#print("MIN CARBON VALUE: {}".format(carbon.min()))
#print("MAX CARBON VALUE: {}".format(carbon.max()))
print("CARBON RANGES FROM {} TO {}.".format(carbon.min(), carbon.max()))

costs = gdf["cost"]

print("COSTS RANGE FROM {} TO {}.".format(costs.min(), costs.max()))

total = 0

for value in carbon:
    total += value

carbon_average = total / 100

#print("AVERAGE CARBON VALUE: {}".format(carbon_average)

# REPROJECTING

gdf = gdf.to_crs(epsg=3347)

# Compute areas
gdf["area_km2"] = gdf.geometry.area / 1e6 # dividing by 10^6 because 1 km^2 = 1 000 000 m^2 = 10^6 m^2

print("AREAS RANGE FROM {} TO {}".format(gdf["area_km2"].min(), gdf["area_km2"].max()))

# filtering outliers
threshold = 0.1
filtered_gdf = gdf[gdf["area_km2"] >= threshold]

print("Polygons removed: {}".format(len(gdf) - len(filtered_gdf)))


adjacency_matrix = np.zeros((len(filtered_gdf), len(filtered_gdf)), dtype=int)


# Check adjacency
for i, geom1 in enumerate(filtered_gdf.geometry):
        for j, geom2 in enumerate(filtered_gdf.geometry):
                    if i != j and geom1.touches(geom2):
                                    adjacency_matrix[i, j] = 1

#print(adjacency_matrix)

filtered_gdf["area"] = filtered_gdf.geometry.area / 1e6

filtered_costs = filtered_gdf['cost']
filtered_carbon = filtered_gdf['carbon_sto']
filtered_areas = filtered_gdf['area']


sumof_costs = filtered_costs.sum()
sumof_areas = filtered_areas.sum()

#print(filtered_gdf.geometry)


parcel_vars = {i: LpVariable("x_{}".format(i), cat = "Binary") for i in range(len(filtered_gdf))}

problem = LpProblem("Maximimze_the_carbon_storage", LpMaximize)

# this is what we need to maximize
problem += lpSum(parcel_vars[i] * filtered_carbon[i] for i in range(len(filtered_gdf)))
#, "Total carbon storage"

# constraint 1 is that budget <= 1/2 total cost
problem += lpSum(filtered_costs[i] * parcel_vars[i] for i in range(len(filtered_gdf))) <= 1/2 * sumof_costs
#, "constraint 1"

# constraint 2 is that no two selected polygons are adjacent
for i in range(len(filtered_gdf)):
    for j in range(len(filtered_gdf)):
        if adjacency_matrix[i, j] == 1:
            # pass
            problem += parcel_vars[i] + parcel_vars[j] <= 1
            #problem += (parcel_vars[i] != 1) or (parcel_vars[j] != 1)

# optional constraint 3 is that the total area of the selected polygons must be >= 1/4 of total area
problem += lpSum(filtered_areas[i] * parcel_vars[i] for i in range(len(filtered_gdf))) >= 1/4 * sumof_areas
#, "constraint 3"

print("---------------------------------Problem optimizing algorithm below------------------------------------")

problem.solve()

print("---------------------------------Problem optimizing algorithm above------------------------------------")

selected_polygons = [i for i in range(len(filtered_gdf)) if parcel_vars[i].value() == 1]

print("{} polygons were selected. View their indexes (in filtered_gdf) below: ".format(len(selected_polygons)))
print(selected_polygons)

for i in selected_polygons:
    for j in selected_polygons:
        if adjacency_matrix[i, j] == 1:

            print(adjacency_matrix[i, j])

#print(adjacency_matrix[selected_polygons[0], i] for i in selected_polygons)

print("Their total carbon storage is {} compared to an overall carbon storage of {}".format(sum(filtered_carbon[i] for i in selected_polygons), filtered_carbon.sum()))

print("Their total cost is {} compared to a budget of {}".format(sum(filtered_costs[i] for i in selected_polygons), 1/2 * sumof_costs))

print("Their total area is {} compared to an overall area of {} (in km^2)".format(sum(filtered_areas[i] for i in selected_polygons), sumof_areas))


print("DONE")



# plotting the terrain

import matplotlib.pyplot as plt

# Create a GeoDataFrame with selected polygons
selected_gdf = filtered_gdf.iloc[selected_polygons]

# Plot the entire filtered GeoDataFrame and then overlay the selected polygons
fig, ax = plt.subplots(figsize=(10, 10))
filtered_gdf.plot(ax=ax, color='lightgrey', edgecolor='black')  # Plot all polygons
selected_gdf.plot(ax=ax, color='green', edgecolor='black')  # Highlight selected polygons in green


plt.title('Selected Polygons')

plt.savefig("selected_polygons_plot.png", bbox_inches='tight')

plt.show()




