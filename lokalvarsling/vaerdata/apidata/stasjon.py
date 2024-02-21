# Funksjoner for å hente værdata fra stasjoner. Hovedsakling met sitt Frost API.
# Funksjonene bruker funksjoner fra frost2df.py for å hente data fra Frost API.
# Frost2df er utviklet av met.no 


import json
from .frost2df import frost2df, obs2df
from datetime import datetime, timedelta
from dateutil import parser, tz
import pandas as pd
import numpy as np


def frost_api(stasjonsid, dager_tidligere, elements, timeoffsets='PT0H'):
    """
    Denne funksjonen henter værdata fra Frost API for en gitt stasjon og tidsperiode.
    Den konverterer svaret til en pandas DataFrame, setter 'referenceTime' som indeksen, sorterer DataFrame etter indeksen,
    og konverterer 'value' kolonnen til numerisk.

    Parametere:
    stasjonsid (str): IDen til stasjonen som dataene skal hentes fra.
    dager_tidligere (int): Antall dager tilbake i tid for å hente data.
    elements (str eller liste): Værelementene som skal hentes. Hvis en liste er gitt, blir den konvertert til en kommaseparert streng.
    timeoffsets (str, valgfritt): Tidsforskyvningene som skal brukes. Standard er 'PT0H'.

    Returnerer:
    df (DataFrame): En DataFrame som inneholder de hentede værdataene.
    """
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    #Finner tidspunkt for xx dager siden
    earlier_date = now - timedelta(days=dager_tidligere)

    # Konverterer til string
    now_str = now.isoformat()
    earlier_date_str = earlier_date.isoformat()

    # Hvis elements er en liste, altså fleire værelementer, konverterer til string
    if type(elements) == list:
        elements = ','.join(elements)

    # Lager parameterene som skal sendes til Frost API
    parameters = {
    'sources':'SN' + str(stasjonsid),
    'elements': elements,
    'referencetime': earlier_date_str + '/' + now_str,
    'timeoffsets': timeoffsets
    }

    # Henter data fra Frost API med hjelp av frost2df pakken
    df = obs2df(parameters=parameters, verbose=True)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    return df



def bearbeid_frost(df):
    """
    Denne funksjonen resampler data til timeverdier for bedre visualisering. 
    Hvis elementet er lufttemperatur, snødybde, vindhastighet eller vindretning, beregnes gjennomsnittet for hver time.
    Hvis elementet er nedbør, summeres nedbøren for hver time.
    Funksjonen returnerer en DataFrame med resamplede verdier for hvert element.

    Parametere:
    df (DataFrame): DataFrame som inneholder data hentet fra Frost API.

    Returnerer:
    df_resampled (DataFrame): DataFrame med resamplede verdier for hvert element.
    """

    # Define the resampling operation for each element
    resampling_operations = {
        'air_temperature': 'mean',
        'surface_snow_thickness': 'mean',
        'wind_speed': 'mean',
        'wind_from_direction': 'mean',
        'sum(precipitation_amount PT10M)': 'sum'
    }

    # Group by 'elementId' and 'referenceTime', then resample and apply the operation for each group
    df_resampled = df.groupby('elementId').resample('H', on='referenceTime').agg({
        'value': lambda group: group.agg(resampling_operations[group.name])
    })
    # Reset the index and replace NaN with None
    df_resampled.reset_index(inplace=True)
    df_resampled['value'] = df_resampled['value'].replace({np.nan: None})

    return df_resampled



def frost_samledf(df):
    df_pivot = df.pivot(index='referenceTime', columns='elementId', values='value')
    return df_pivot


def assign_direction_to_bin(value):
    if value >= 337.5 or value < 22.5:
        return 'N'
    elif value < 67.5:
        return 'NØ'
    elif value < 112.5:
        return 'Ø'
    elif value < 157.5:
        return 'SØ'
    elif value < 202.5:
        return 'S'
    elif value < 247.5:
        return 'SV'
    elif value < 292.5:
        return 'V'
    elif value < 337.5:
        return 'NV'

def vindrose(stasjonsid, dager_tidligere):
    """
    Denne funksjonen henter vindhastighet og vindretning fra Frost API for en gitt stasjon og tidsperiode.
    Den kombinerer deretter disse dataene i en enkelt DataFrame, og kategoriserer vindhastigheten og vindretningen i binner.
    Til slutt, den returnerer en pivotert DataFrame som viser frekvensen av vindhastighet og retning kombinasjoner.

    Parametere:
    stasjonsid (str): IDen til stasjonen som dataene skal hentes fra.
    dager_tidligere (int): Antall dager tilbake i tid for å hente data.

    Returnerer:
    pivot_df (DataFrame): En DataFrame som viser frekvensen av vindhastighet og retning kombinasjoner.
    """
    direction_order = ['N', 'NØ', 'Ø', 'SØ', 'S', 'SV', 'V', 'NV']

    df_wind_speed = frost_api(stasjonsid, dager_tidligere, 'wind_speed', timeoffsets='PT0H')
    df_wind_from_direction = frost_api(stasjonsid, dager_tidligere, 'wind_from_direction', timeoffsets='PT0H')
    df_wind_speed = df_wind_speed.rename(columns={'value': 'wind_speed'})
    df_wind_from_direction = df_wind_from_direction.rename(columns={'value': 'wind_from_direction'})

    df_combined = df_wind_speed[['wind_speed']].merge(df_wind_from_direction[['wind_from_direction']], left_index=True, right_index=True)


    speed_bins = [0, 4, 8, 11, 14, 17, 20, 25, float('inf')]
    speed_labels = ['0-4 m/s', '4-8 m/s', '8-11 m/s', '11-14 m/s', '14-17 m/s', '17-20 m/s', '20-25 m/s', '>25 m/s']

    df_combined['direction_bin'] = df_combined['wind_from_direction'].apply(assign_direction_to_bin)
    df_combined['speed_bin'] = pd.cut(df_combined['wind_speed'], bins=speed_bins, labels=speed_labels, right=True)

    frequency_2d_df = df_combined.groupby(['direction_bin', 'speed_bin']).size().reset_index(name='Frequency')

  # Pivot the table to have wind speeds as columns and directions as rows
    pivot_df = frequency_2d_df.pivot(index='direction_bin', columns='speed_bin', values='Frequency')

    # Replace NaNs with 0s and ensure all direction bins are present
    pivot_df = pivot_df.reindex(direction_order, fill_value=0)

    # Convert the index to a categorical with the specified order
    pivot_df.index = pd.CategoricalIndex(pivot_df.index, categories=direction_order, ordered=True)

    # Sorting by index is not needed since reindexing has already ordered the index as per `direction_order`

    # Printing the pivot_df for verification
    print(pivot_df)

    return pivot_df

    