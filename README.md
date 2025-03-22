
Reads land_parcel.shp and discovers the optimal subset of polygons based on a few constraints. We want the subset with the largest total carbon store, that satisfies the 3 following constraints:

Constraint 1: The total cost of selected polygons must be less that half the total cost of all polygons.

Constraint 2: No 2 selected polygons can share an edge or point.
