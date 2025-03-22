# About
Reads land_parcel.shp and discovers the optimal subset of polygons based on a few constraints. We want the subset with the largest total carbon store, that satisfies the 3 following constraints:

Constraint 1: The total cost of selected polygons must be less that half the total cost of all polygons.

Constraint 2: No 2 selected polygons can share an edge or point.

Constraint 3: The total area of selected polygons must be at least 1/4 the area of all polygons.

# Output
Run main.c to see the text output.

The output has also been plotted in 3 graphs:

selected_polygons_plot_1.png displays the optimal subset with only constraint 1 applied

selected_polygons_plot_2.png displays the optimal subset with constraints 1 and 2 applied

selected_polygons_plot_3.png displays the optimal subset with all (1, 2 and 3) constraints applied

# Setup

- Create a new folder with main.c, and the land_parcel files (ensure they are all in the same folder by taking them out of the terrain_files folder)
- Install geopandas, pulp with pip: pip install geopandas pulp
- Run main.c
  
