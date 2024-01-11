# %%
from shapely.geometry import Polygon, LineString, MultiPoint, Point
import geopandas as gpd
import matplotlib.pyplot as plt

s = gpd.GeoSeries(
    [
        Polygon([(0, 0), (2, 2), (0, 2)]),
        # Polygon([(0, 0), (2, 2), (0, 2)]),
        # LineString([(0, 0), (2, 2)]),
        # MultiPoint([(0, 0), (0, 1)]),
    ],
)
s1 = gpd.GeoSeries(
    [
        Polygon([(0.5, 0.5), (1.5, 1.5), (0.5, 1.5)]),
        # Polygon([(0, 0), (2, 2), (0, 2)]),
        # LineString([(0, 0), (2, 2)]),
        # MultiPoint([(0, 0), (0, 1)]),
    ],
)
s2 = gpd.GeoSeries(
    [
        Polygon([(0, 0), (2, 2), (2, 0)]),
        # LineString([(0, 1), (1, 1)]),
        # LineString([(1, 1), (3, 0)]),
        # Point(0, 1),
    ],
)
s3 = gpd.GeoSeries(
    [
        Polygon([(0.2, 0.2), (-1.9, 0.2), (0.2, -1.8)]),
        # LineString([(0, 1), (1, 1)]),
        # LineString([(1, 1), (3, 0)]),
        # Point(0, 1),
    ],
)

s4 = gpd.GeoSeries(
    [
        Polygon([(-0.2, 0.2), (-1.9, 0.2), (-0.2, -1.8)]),
        # LineString([(0, 1), (1, 1)]),
        # LineString([(1, 1), (3, 0)]),
        # Point(0, 1),
    ],
)

s5 = gpd.GeoSeries(
    [
        Polygon([(5, 5), (7, 7), (8, 8)]),
        # LineString([(0, 1), (1, 1)]),
        # LineString([(1, 1), (3, 0)]),
        # Point(0, 1),
    ],
)


# %%
print(s.touches(s2))
print(s.overlaps(s2))
print(s.intersects(s2))

# %%
print(s.touches(s3))
print(s.overlaps(s3))
print(s.intersects(s3))


# %%
print(s3.touches(s))
print(s3.overlaps(s))
print(s3.intersects(s))

# %%
print(s.touches(s2))
print(s.overlaps(s2))
print(s.intersects(s2))
print(s.covers(s2))

# %%
print(s.intersection(s).is_ring)
print(s.intersection(s2).is_ring)
print(s.intersection(s3).is_ring)
print(s.intersection(s4).is_ring)

# %%
print(s.intersection(s))
print(s.intersection(s2))
print(s.intersection(s3))
print(s.intersection(s4))
print(s.intersection(s5))


# %%
print(s.intersection(s).area > 0)
print(s.intersection(s2).area > 0)
print(s.intersection(s3).area > 0)
print(s.intersection(s4).area > 0)
print(s.intersection(s5).area > 0)

# %%
print(s.intersects(s))
print(s.intersects(s2))
print(s.intersects(s3))
print(s.intersects(s4))
print(s.intersects(s5))

# %%
print(s.touches(s))
print(s.touches(s2))
print(s.touches(s3))
print(s.touches(s4))
print(s.touches(s5))

# %%
