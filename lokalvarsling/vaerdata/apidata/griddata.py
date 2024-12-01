import requests
import pandas as pd
import datetime

PARAMETERS = {
    "rr": "Døgnnedbør",
    "rr3h": "Nedbør 3 timer",
    "rrl": "Regn",
    "rrprrxrm5": "Nedbør i % av 5 år",
    "tm": "Temperatur",
    "tm3h": "Temperatur 3 timer",
    "tmgr": "Temperaturendring",
    "swe": "Snømengde",
    "swepr": "Snømengde i prosent",
    "swechange7d": "Snø endring siste uke",
    "swerank": "Snømengde rangert",
    "snowload": "Snølast",
    "age": "Snøens alder",
    "lwc": "Snøtilstand",
    "fsw": "Nysnø siste døgn",
    "fsw7d": "Nysnø siste uke",
    "sdfsw": "Nysnødybde",
    "sdfsw7d": "Nysnødybde 7 døgn",
    "sdfsw3d": "Nysnødybde 3 døgn",
    "additional_snow_depth": "Fokksnøindeks",
    "qsw": "Snøsmelting siste døgn",
    "qsw7d": "Snøsmelting sum siste uke",
    "qtt": "Regn og snøsmelting",
    "qtt7d": "Regn og snøsmelting siste uke",
    "qttls": "Vanntilførsel",
    "qtt3dls": "Vanntilførsel 3 døgn",
    "gwb_qtt": "HBV Vanntilførsel",
    "gwb_qtt3d": "HBV Vanntilførsel 3 døgn",
    "gwb_qtt3dlst": "Vanntilførsel 3 døgn",
    "gwb_qttprrxm200": "Vanntilførsel 1 døgn i % av 200 år",
    "gwb_qtt3dprrxm200": "Vanntilførsel 3 døgn i % av 200 år",
    "gwb_qttprgwb_qttyxrx30yr": "Vanntilførsel 1 døgn i % maks",
    "gwb_qtt3dprgwb_qtt3dxyrx30yr": "Vanntilførsel 3 døgn i % maks",
    "gwb_gwt": "Grunnvann",
    "gwb_gwtdev": "Døgnendring grunnvann",
    "gwb_gtwtyxrx30yr": "Grunnvann i % av maksimum",
    "gwb_q": "Avrenning",
    "gwb_qprgwb_qxyxrx30yr": "Avrenning i % av maksimum",
    "gwb_eva": "Fordamping",
    "gwb_sssdev": "Jordas vannkapasitet",
    "gwb_frd": "Teledyb",
    "gwb_sssrel": "Vannmetning",
    "gwb_landslideindex1": "Jordskredindeks1",
    "gwb_landslideindex2": "Jordskredindeks2",
    "indDirection10m3h": "Vindretning 10m 3 timer",
    "windSpeed10m24h06": "Vindhastighet 10m døgn",
    "windSpeed10m3h": "Vindhastighet 10m 3 timer",
    "qsweenergy": "Snøsmelting fra energibalanse modell",
    "qsweenergy3h": "Snøsmelting 3 timer fra energibalanse modell"
}

def nve_api(x: str, y: str, startdato: str, sluttdato: str, para: str) -> list:
    """Henter data frå NVE api GridTimeSeries

    Parameters
    ----------
        x 
            øst koordinat (i UTM33)
        y  
            nord koordinat (i UTM33)
        startdato
            startdato for dataserien som hentes ned
        sluttdato 
            sluttdato for dataserien som hentes ned
        para
            kva parameter som skal hentes ned f.eks rr for nedbør

    Returns
    ----------
        verdier
            returnerer ei liste med klimaverdier

    """
    api = "http://h-web02.nve.no:8080/api/"
    url = (
        api
        + "/GridTimeSeries/"
        + str(x)
        + "/"
        + str(y)
        + "/"
        + str(startdato)
        + "/"
        + str(sluttdato)
        + "/"
        + para
        + ".json"
    )
    r = requests.get(url)
    print(f"Request URL: {url}")
    print(f"Response status code: {r.status_code}")
    #print(f"Response text: {r.text}")
    verdier = r.json()
    print(verdier)
    return verdier

def klima_dataframe(x, y, startdato, sluttdato, parametere) -> pd.DataFrame:
    """Lager dataframe basert på klimadata fra NVE api.

    Bruker start og sluttdato for å generere index i pandas dataframe.

    Parameters
    ----------
        x
            øst-vest koordinat (i UTM33)
        y
            nord-sør koordinat (i UTM33)
        startdato
            startdato for dataserien som hentes ned
        sluttdato
            sluttdato for dataserien som hentes ned
        parametere
            liste med parametere som skal hentes ned f.eks rr for nedbør

    Returns
    ----------
        df
            Pandas dataframe med klimadata

    """
    print('klima dataframe stareter')
    parameterdict = {}
    for parameter in parametere:

        parameterdict[parameter] = nve_api(x, y, startdato, sluttdato, parameter)[
            "Data"
        ]
    print('parameterdict', parameterdict)
    df = pd.DataFrame(parameterdict)
    df = df.set_index(
        #Setter index til å være dato, basert på start og sluttdato
        pd.date_range(
            datetime.datetime(
                int(startdato[0:4]), int(startdato[5:7]), int(startdato[8:10])
            ),
            datetime.datetime(
                int(sluttdato[0:4]), int(sluttdato[5:7]), int(sluttdato[8:10])
            ),
        )
    )
    df[df > 1000] = 0 #Kutter ut verdier som er større enn 1000, opprydding
    return df

