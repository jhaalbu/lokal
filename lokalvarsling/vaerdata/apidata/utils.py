from pyproj import Proj, transform

def utm_to_latlon(easting, northing, zone_number, zone_letter):
    ''' OBS! må skrives om til pyproj 2 format:
    https://pyproj4.github.io/pyproj/stable/gotchas.html#upgrading-to-pyproj-2-from-pyproj-1
    '''
    utm_proj = Proj(proj='utm', zone=zone_number, ellps='WGS84', south=(zone_letter < 'N'))
    latlon_proj = Proj(proj='latlong', datum='WGS84')
    longitude, latitude = transform(utm_proj, latlon_proj, easting, northing)
    return latitude, longitude

def sjekk_element_ids(json_data, elements):
    """
    Sjekker om noen elementId-verdier fra JSON-data finnes i en liste av elementer.

    Args:
        json_data (dict): JSON-datastruktur.
        elements (list): Liste over elementer som skal sjekkes mot.

    Returns:
        list: Liste over elementId-verdier som finnes i både JSON-data og elementlisten.
    """
    # Hent 'data'-nøkkelen fra JSON-strukturen
    data = json_data.get("data", [])
    
    # Samle elementId-verdier fra JSON-data
    element_ids = {item.get("elementId") for item in data if "elementId" in item}
    
    # Finn elementId-verdier som finnes i begge lister
    felles_elementer = [eid for eid in element_ids if any(eid.startswith(elem) for elem in elements)]
    
    return felles_elementer