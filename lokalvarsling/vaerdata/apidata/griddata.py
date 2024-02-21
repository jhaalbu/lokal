import requests
import pandas as pd
import datetime

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

    verdier = r.json()
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
    parameterdict = {}
    for parameter in parametere:

        parameterdict[parameter] = nve_api(x, y, startdato, sluttdato, parameter)[
            "Data"
        ]

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