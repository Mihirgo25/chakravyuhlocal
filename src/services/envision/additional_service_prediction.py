import geopy.distance

def get_distance(cord1, cord2):
    coords_1 = cord1
    coords_2 = cord2
    return geopy.distance.geodesic(coords_1, coords_2).km

