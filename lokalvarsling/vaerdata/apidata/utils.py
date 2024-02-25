from pyproj import Proj, transform

def utm_to_latlon(easting, northing, zone_number, zone_letter):
    utm_proj = Proj(proj='utm', zone=zone_number, ellps='WGS84', south=(zone_letter < 'N'))
    latlon_proj = Proj(proj='latlong', datum='WGS84')
    longitude, latitude = transform(utm_proj, latlon_proj, easting, northing)
    return latitude, longitude