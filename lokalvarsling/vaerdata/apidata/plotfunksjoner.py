import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import pi, cos, sin
import math
from metno_locationforecast import Place, Forecast
from .met import metno_forecast_to_dataframe
from .stasjon import frost_api, vindrose, bearbeid_frost, frost_samledf, hent_stasjonsinfo
from .griddata import klima_dataframe, hent_hogde, stedsnavn

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
    "windDirection10m24h06": "Vindretning 10m døgn",
    "windDirection10m3h": "Vindretning 10m 3 timer",
    "windSpeed10m24h06": "Vindhastighet 10m døgn",
    "windSpeed10m3h": "Vindhastighet 10m 3 timer",
    "qsweenergy": "Snøsmelting fra energibalanse modell",
    "qsweenergy3h": "Snøsmelting 3 timer fra energibalanse modell"
    }

user_agent = "Stedspesifikk v/0.1 jan.helge.aalbu@vegvesen.no"

#Meir fleksibel plotfunksjoner

def hent_yr_data(lat, lon, navn, altitude, dager_etter_met, user_agent):
    vaer = Place(navn, lat, lon, altitude)
    vaer_forecast = Forecast(vaer, user_agent)
    vaer_forecast.update()
    met_df = metno_forecast_to_dataframe(vaer_forecast, dager_etter_met)
    return met_df.resample('1h').mean()

def hent_frost_data(stasjonsid, dager_tidligere_frost, elements):
    df = frost_api(stasjonsid, dager_tidligere_frost, elements, timeoffsets='PT0H')
    df_bearbeida = bearbeid_frost(df)
    return frost_samledf(df_bearbeida)

def sett_opp_fig_layout(precipitation=False, wind=False, snow=False):
    """
    Konfigurer layout for figuren dynamisk basert på hvilke data som skal vises.
    
    Args:
        wind (bool): Inkluder vinddata som en egen rad hvis True.
        snow (bool): Inkluder snødata som en egen rad hvis True.

    Returns:
        fig (plotly.graph_objects.Figure): Figuren med definert layout.
        plotheight (int): Høyden på figuren.
        showticklabels_row2 (bool): Om aksetiketter skal vises på rad 2.
    """
    # Konfigurer antall rader basert på hvilke data som er tilgjengelig
    if wind and snow:
        print('wind and snow')
        rows = 3
        row_heights = [0.5, 0.25, 0.3]
        specs = [[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]]
        plotheight = 700
    elif snow:
        print('snow')
        rows = 2
        row_heights = [0.5, 0.5]
        specs = [[{"secondary_y": True}], [{"secondary_y": True}]]
        plotheight = 600
    elif wind:
        print('wind')
        rows = 2
        row_heights = [0.7, 0.3]
        specs = [[{"secondary_y": True}], [{"secondary_y": True}]]
        plotheight = 500
    else:
        print('no wind or snow')
        rows = 1
        row_heights = [1.0]
        specs = [[{"secondary_y": True}]]
        plotheight = 400

    # Opprett subplot-konfigurasjon
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.01,
        row_heights=row_heights,
        specs=specs
    )
    
    # Konfigurer etiketter på rad 2 (vis kun hvis det finnes minst to rader)
    showticklabels_row2 = rows > 1

    return fig, plotheight, showticklabels_row2

def legg_til_yr_precipitation(fig, met_df, row, col):
    """
    Legger til YR-nedbør med stripete søyler i figuren.

    Args:
        fig: Plotly-figur.
        met_df: DataFrame med YR-data.
        row: Rad hvor nedbørsdata skal plottes.
        col: Kolonne hvor nedbørsdata skal plottes.

    Returns:
        fig: Oppdatert figur.
    """
    # Legg til YR-nedbør (sekundærakse) med stripete mønster
    fig.add_trace(go.Bar(
        x=met_df.index,
        y=met_df['Precipitation'],
        name='Nedbør (YR)',
        width=1000 * 3600,
        marker=dict(
            color='rgba(0, 123, 255, 0.5)',  # Bakgrunnsfarge
            pattern=dict(
                shape='/',  # Stripete mønster (skråstreker)
                fgcolor='rgba(0, 0, 255, 0.8)'  # Farge på stripene
            )
        )
    ), row=row, col=col, secondary_y=True)

    return fig

def legg_til_yr_kumulativ_precipitation(fig, met_df, row, col):

    # Prepare custom hover text with the actual 'Cumulative Precipitation' values
    hover_text = ['Kumulativ nedbør: {:.2f}'.format(p) for p in met_df['Cumulative Precipitation']]

    fig.add_trace(go.Scatter(
        x=met_df.index,
        y=met_df['Cumulative Precipitation'],
        mode='lines',
        name='Kumulativ nedbør (YR)',
        fill='tozeroy',
        line=dict(color='rgba(50, 235, 216, 0.5)', dash='dot'),
        fillcolor='rgba(50, 235, 216, 0.1)',
        text=hover_text,  # Use custom text for hover
        hoverinfo='text+x'
    ), row=row, col=col, secondary_y=True)

    return fig

def leg_til_frost_kumulativ_precipitation(fig, samledf, row, col):


    fig.add_trace(go.Scatter(
        x=samledf.index,
        y=samledf['accumulated_precipitation'],
        mode='lines',
        name='Kumulativ nedbør (Frost)',
        fill='tozeroy',
        line=dict(color='rgba(50, 235, 216, 0.5)', dash='dot'),
        fillcolor='rgba(50, 235, 216, 0.1)'
    ), row=row, col=col, secondary_y=True)

    return fig

def legg_til_frost_precipitation(fig, samledf, row, col):
    """
    Legger til nedbør på figuren.

    Args:
        fig: Plotly-figur.
        samledf: DataFrame med Frost-data.
        met_df: DataFrame med YR-data.
        row: Rad hvor nedbørsdata skal plottes.
        col: Kolonne hvor nedbørsdata skal plottes.

    Returns:
        fig: Oppdatert figur.
    """

    # Legg til Frost-nedbør
    fig.add_trace(go.Bar(
        x=samledf.index,
        y=samledf['sum(precipitation_amount PT10M)'],
        name='Nedbør (Frost)',
        width=1000 * 3600,
        marker_color='rgba(0, 123, 255, 0.8)'),
        row=row, col=col, secondary_y=True)

    return fig

def legg_til_yr_temperatur(fig, met_df):
    for i in range(len(met_df) - 1):
        color = 'red' if met_df['Temperature'][i] >= 0 else 'blue'
        fig.add_trace(go.Scatter(x=met_df.index[i:i+2], y=met_df['Temperature'][i:i+2],
                                 mode='lines', line=dict(color=color, width=2, dash='dot'), 
                                 showlegend=False), row=1, col=1)
    return fig

def legg_til_frost_temperatur(fig, samledf):
    for i in range(len(samledf) - 1):
        color = 'red' if samledf['air_temperature'][i] >= 0 else 'blue'
        fig.add_trace(go.Scatter(x=samledf.index[i:i+2], y=samledf['air_temperature'][i:i+2], 
                                 mode='lines', line=dict(color=color, width=2), 
                                 showlegend=False), row=1, col=1)
    
    fig.update_yaxes(title_text='Temperatur', title_font=dict(size=12, color='black'),
                tickfont=dict(size=12, color='black'),showgrid=True, row=1, col=1)
    
    return fig

def legg_til_snow(fig, samledf, row, col):
    """
    Legger til snødjupne på figuren.

    Args:
        fig: Plotly-figur.
        samledf: DataFrame med Frost-data.
        row: Rad hvor snødata skal plottes.
        col: Kolonne hvor snødata skal plottes.

    Returns:
        fig: Oppdatert figur.
    """
    fig.add_trace(go.Scatter(
        x=samledf.index,
        y=samledf['surface_snow_thickness'],
        name='Snødjupne',
        mode='lines',
        line=dict(color='cyan', dash='solid')
    ), row=row, col=col)

    # Oppdater y-aksen for snø
    fig.update_yaxes(
        title_text="Snødjupne (cm)",
        title_font=dict(size=12, color='cyan'),
        tickfont=dict(size=12, color='cyan'),
        row=row, col=col,
        showgrid=True
    )
    return fig

def legg_til_frost_wind(fig, samledf, row, col):
    """
    Legger til vindhastighet

    Args:
        fig: Plotly-figur.
        samledf: DataFrame med Frost-data.
        row: Rad hvor vinddata skal plottes.
        col: Kolonne hvor vinddata skal plottes.

    Returns:
        fig: Oppdatert figur.
    """
    # Legg til vindhastighet
    fig.add_trace(go.Scatter(
        x=samledf.index,
        y=samledf['wind_speed'],
        name='Vindhastighet',
        mode='lines',
        line=dict(color='purple', dash='solid')
    ), row=row, col=col)

    # Oppdater y-aksen for vind
    fig.update_yaxes(
        title_text="Vindhastighet (m/s)",
        title_font=dict(size=12, color='purple'),
        tickfont=dict(size=12, color='purple'),
        row=row, col=col,
        showgrid=True,
        range=[0,30]
    )
    return fig

def leg_til_yr_vind(fig, met_df, row=2, col=1):
    for i in range(len(met_df) - 1):
        fig.add_trace(go.Scatter(x=met_df.index[i:i+2], y=met_df['Wind Speed'][i:i+2],
                                 mode='lines', line=dict(color='purple', width=2, dash='dot'), 
                                 showlegend=False), row=row, col=col)
    return fig

def legg_til_yr_vindpiler(fig, met_df, row=2, col=1):
    for time, data in met_df.iterrows():
        radian = math.radians(data['Wind Direction'])
        fig.add_annotation(
            x=time,
            y=0,  # Sett en passende y-posisjon for pilene dine
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor='black',
            ax=20 * sin(radian),
            ay=-20 * cos(radian),
            row=row, col=col  #  * -1 Plotly's koordinatsystem er invertert for y
            )
    return fig

def legg_til_frost_vindpiler(fig, df_resampled, row, col):
    for time, row_data in df_resampled.iterrows():
        radian = row_data['wind_from_direction'] * (pi / 180)
        fig.add_annotation(
            x=time,
            y=0,  # Sett en passende y-posisjon for pilene
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor='black',
            ax=20 * cos(radian),
            ay=-20 * sin(radian),
            row=row, col=col
        )
    return fig



def plotfunksjon_stasjon_ny(lat, lon, navn, altitude, stasjonsid, elements, dager_etter_met, dager_tidligere_frost, 
                         percipitation=False, wind=False, snow=False):
    # Hent og bearbeid data
    met_df = hent_yr_data(lat, lon, navn, altitude, dager_etter_met, user_agent)
    samledf = hent_frost_data(stasjonsid, dager_tidligere_frost, elements)
    df_resampled = samledf.resample('3h').mean()
    print(samledf)
    met_df_resampled = met_df.resample('3h').mean()

    # Sett opp plottet
    fig, plotheight, row_config = sett_opp_fig_layout(wind=wind, snow=snow, precipitation=percipitation)

    # Legg til YR-data

    fig = legg_til_yr_temperatur(fig, met_df)

    # Legg til Frost-data
    fig = legg_til_frost_temperatur(fig, samledf)

    if percipitation:
        fig = legg_til_frost_precipitation(fig, samledf, row=1, col=1)
        fig = legg_til_yr_precipitation(fig, met_df, row=1, col=1)
        #legg_til_yr_kumulativ_precipitation(fig, met_df, row=1, col=1)
        #leg_til_frost_kumulativ_precipitation(fig, samledf, row=1, col=1)
            # Oppdater y-aksen for nedbør
        fig.update_yaxes(
            title_text="Nedbør (mm)",
            title_font=dict(size=12, color='blue'),
            tickfont=dict(size=12, color='blue'),
            row=1, col=1,
            secondary_y=True,
            overlaying="y",
            showgrid=False,
            range=[0, 8]
        )

    # Legg til vinddata, hvis tilgjengelig
    if wind:
        fig = legg_til_frost_wind(fig, samledf, row=2, col=1)
        fig = legg_til_frost_vindpiler(fig, df_resampled, row=2, col=1)
        fig = legg_til_yr_vindpiler(fig, met_df_resampled, row=2, col=1)
        fig = leg_til_yr_vind(fig, met_df, row=2, col=1)

    # Legg til snødata, hvis tilgjengelig
    if snow:
        fig = legg_til_snow(fig, samledf, row=3 if wind else 2, col=1)

    # Oppdater layout
    fig.update_layout(
        title={
            'text': f"{navn} - {altitude} moh. - ID: {stasjonsid}",
            'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'
        },
        title_font=dict(family="Arial, sans-serif", size=24, color="black"),
        autosize=True, height=plotheight, showlegend=False
    )

    return fig


def plotfunksjon_griddata(x, y, startdato, sluttdato, parametere=["rr", "rrl", "tm", "lwc", "fsw", "fsw7d", "sdfsw", "sdfsw7d", "sdfsw3d", "windDirection10m24h06", "windSpeed10m24h06"]):
    print('plotfunksjon starter')

    df = klima_dataframe(x, y, startdato, sluttdato, parametere)
    altitude = hent_hogde(x, y)
    print(df)     
    try:
        sted = stedsnavn(x, y)
    except:
        sted = ' '
        
    # Lag subplots
    fig = make_subplots(
        rows=4, cols=1,
        row_heights = [0.4, 0.2, 0.2, 0.2],
        specs = [[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]],
        shared_xaxes=True,
        vertical_spacing=0.01
    )

    for i in range(len(df) - 1):
        color = 'red' if df['tm'][i] >= 0 else 'blue'
        fig.add_trace(go.Scatter(x=df.index[i:i+2], y=df['tm'][i:i+2], 
                                 mode='lines', line=dict(color=color, width=2), 
                                 showlegend=False), row=1, col=1)
    
    fig.update_yaxes(
        title_text="Temperatur (°C)",
        title_font=dict(size=12, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=True,
        range=[df['tm'].min() - 2, df['tm'].max() + 2],  # Temperatur-intervall
        row=1, col=1,
        secondary_y=False
    )

    # Oppdater y-akse for nedbør (sekundærakse)
    fig.update_yaxes(
        title_text="Nedbør (mm)",
        title_font=dict(size=12, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=False,
        overlaying="y",
        side="right",
        range=[-2, df[['rrl', 'fsw']].max().max() + 2],  # Maks av 'rrl' og 'fsw'
        row=1, col=1,
        secondary_y=True
    )

    fig.update_yaxes(
        title_text="Nysnødybde (cm)",
        title_font=dict(size=12, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=True,
        range=[-2, df[['sdfsw7d', 'sdfsw3d']].max().max() + 2],
        row=2, col=1,
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Snøtilstand <br> (% fritt vann)",
        title_font=dict(size=12, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=True,
        range=[-2, 12],
        row=3, col=1,
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Vindhastighet (m/s)",
        title_font=dict(size=12, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=True,
        range=[0, df['windSpeed10m24h06'].max() * 1.5],
        row=4, col=1,
        secondary_y=False
    )


    # Legg til regn (søyle)
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["rrl"],
            name=PARAMETERS["rrl"],
            marker_color='rgba(0, 123, 255, 0.8)',
            width=1000 * 3600 * 24 / 2,
        ),
        row=1, col=1, secondary_y=True
    )

    # Legg til snø (søyle)
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["fsw"],
            name=PARAMETERS["fsw"],
            marker_color='rgba(120, 200, 230, 0.8)',
            width=1000 * 3600 * 24 / 2,
        ),
        row=1, col=1, secondary_y=True
    )

    # Andre subplot: Nysnødybde 3 døgn (søyler) og Nysnødybde 7 døgn (linje)
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["sdfsw3d"],
            name=PARAMETERS["sdfsw3d"],
            marker_color='rgba(120, 200, 230, 0.8)',
            width=1000 * 3600 * 24 / 2,
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["sdfsw7d"],
            mode="lines",
            name=PARAMETERS["sdfsw7d"],
            line=dict(color='rgba(120, 200, 230, 0.8)')
        ),
        row=2, col=1
    )

    # Tredje subplot: Snøtilstand (linje)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["lwc"],
            mode="lines",
            name=PARAMETERS["lwc"],
            line=dict(color="brown")
        ),
        row=3, col=1
    )

    # Oppsett av aksene og layout
    fig.update_layout(
        title=f"Griddata for {sted} ({x}, {y}) - {altitude} moh.",
        height=800,
        showlegend=False,
        legend_title="Parametere",
    )

    fig.update_layout(
        title={
            'text': f"Griddata for {sted} ({x}, {y}) - {altitude} moh.",
            'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'
        },
        title_font=dict(family="Arial, sans-serif", size=24, color="black"),
        autosize=True, height=700, showlegend=False
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["windSpeed10m24h06"],
            mode="lines",
            name=PARAMETERS["windSpeed10m24h06"],
            line=dict(color="purple")
        ),
        row=4, col=1
    )

    for time, row_data in df.iterrows():
        radian = math.radians(row_data['windDirection10m24h06'] - 90)
        fig.add_annotation(
            x=time,
            y=0,  # Sett en passende y-posisjon for pilene
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor='black',
            ax=20 * cos(radian),
            ay=20 * sin(radian),
            row=4, col=1
        )


    return fig

def plotfunksjon_stasjon(lat, lon, navn, altitude, stasjonsid, elements, dager_etter_met, dager_tidligere_frost, percipitation=False, wind=False, snow=False, ):   
    '''Denne funksjonen er kunn til bruk for testing, brukes ikkje i produksjon'''
    # Henter data fra YR for ein gitt koordinat
    vaer = Place(navn, lat, lon, altitude)
    vaer_forecast = Forecast(vaer, user_agent)
    vaer_forecast.update()

    # Bearbeider nedhenta data fra yr og lager df for enkel plotting

    met_df = metno_forecast_to_dataframe(vaer_forecast, dager_etter_met)

    df_met_resampled = met_df.resample('3h').mean()
    

    # Henter data fra frost for ein gitt stasjon

    df = frost_api(stasjonsid, dager_tidligere_frost, elements, timeoffsets='PT0H')
    df_bearbeida = bearbeid_frost(df)
    samledf = frost_samledf(df_bearbeida)
    
    # Bearbeiding av data for å få tilpassa plott, vindpiler..
    df_resampled = samledf.resample('3h').mean()

    positive_temperature_frost = np.where(samledf['air_temperature'] > 0, samledf['air_temperature'], np.nan)
    negative_temperature_frost = np.where(samledf['air_temperature'] <= 0, samledf['air_temperature'], np.nan)


    # Definerer farger for plottet
    # TODO: Berre delvis brukt, kan fjernast?
    temperature_color = 'rgba(255, 165, 0, 0.8)'  # orange
    precipitation_color = 'rgba(0, 123, 255, 0.8)'  # blue
    wind_color = 'rgba(178, 39, 245, 0.8)'  # lilla
    snow_color = 'rgba(52, 204, 235, 0.8)'  # cyan
  

          

    # Lager hovedfigur
    fig = go.Figure()

    if wind == False:
        fig_rows = 1
    if snow:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.4, 0.3, 0.3], specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]])
        plotheight = 700
        showticklabels_row2 = False
    else:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.6, 0.4], specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
        plotheight = 500
        showticklabels_row2 = True
    
    fig.update_xaxes(showticklabels=False, showgrid=True, row=1, col=1)
    fig.update_xaxes(showticklabels=showticklabels_row2, showgrid=True, row=2, col=1)

    # Plotter fra YR, samle alt i ein dataframe?

    fig.add_trace(go.Bar(x=met_df.index, y=met_df['Precipitation'], name='Nedbør (YR)', width=1000 * 3600,
                         marker_color=precipitation_color), row=1, col=1, secondary_y=True)

    for i in range(len(met_df) - 1):
        # Determine the color based on the temperature value
        if met_df['Temperature'][i] >= 0:
            color = 'red'
        else:
            color = 'blue'
        
        # Plot each segment
        fig.add_trace(go.Scatter(x=met_df.index[i:i+2], y=met_df['Temperature'][i:i+2],
                                mode='lines', line=dict(color=color, width=2, dash='dot'),
                                showlegend=False), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=met_df.index, y=met_df['Wind Speed'], mode='lines',
                             name='Vind (YR)', line=dict(color=wind_color, dash='dot')), row=2, col=1)
    

    # Plotting kumulativ nedbør fra YR
    scaled_precipitation = met_df['Cumulative Precipitation'] / 3

# Prepare custom hover text with the actual 'Cumulative Precipitation' values
    hover_text = ['Kumulativ nedbør: {:.2f}'.format(p) for p in met_df['Cumulative Precipitation']]

    fig.add_trace(go.Scatter(x=met_df.index, y=scaled_precipitation,
                            mode='lines', name='Kumulativ nedbør (YR)', fill='tozeroy',
                            line=dict(color='rgba(50, 235, 216, 0.5)', dash='dot'),
                            fillcolor='rgba(50, 235, 216, 0.1)',
                            text=hover_text, hoverinfo='text+x'), row=1, col=1, secondary_y=True)  # Use custom text for hover


    # fig.add_trace(go.Scatter(x=met_df.index, y=met_df['Cumulative Precipitation'], mode='lines',
    #                         name='Kumulativ nedbør (YR)', fill='tozeroy',
    #                         line=dict(color='blue', dash='dot'),
    #                         fillcolor='rgba(50, 150, 255, 0.1)'), row=1, col=1, secondary_y=True)


    # Plotter fra stasjon, Frost. Dette er fra ein dataframe
    for i in range(len(samledf) - 1):
        # Determine the color based on the temperature value
        if samledf['air_temperature'][i] >= 0:
            color = 'red'
        else:
            color = 'blue'
        
        # Plot each segment
        fig.add_trace(go.Scatter(x=samledf.index[i:i+2], y=samledf['air_temperature'][i:i+2], name='Temperatur (målt)',
                                mode='lines', line=dict(color=color, width=2),
                                showlegend=False), row=1, col=1)
    # fig.add_trace(go.Scatter(
    #     x=samledf.index, y=positive_temperature_frost, mode='lines',
    #     name='Temperatur - målt', line=dict(color='red')), row=1, col=1)

    # fig.add_trace(go.Scatter(
    #     x=samledf.index, y=negative_temperature_frost, mode='lines',
    #     name='Temperatur - målt', line=dict(color='blue')), row=1, col=1)
    
    if percipitation:
        fig.add_trace(go.Bar(x=samledf.index, y=samledf['sum(precipitation_amount PT10M)'],
                            name='Nedbør (målt)', width=1000 * 3600, marker_color=precipitation_color), row=1, col=1, secondary_y=True)

    if wind:
        fig.add_trace(go.Scatter(x=samledf.index, y=samledf['wind_speed'], name='Vindhastighet (målt)',
                                mode='lines', line=dict(color=wind_color)), row=2, col=1) 
    
    if snow:
        fig.add_trace(go.Scatter(x=samledf.index, y=samledf['surface_snow_thickness'], name='Snødjupne (målt)',
                                mode='lines', line=dict(color=snow_color)), row=3, col=1)
        fig.update_yaxes(title_text='Snødjupne (cm)', title_font=dict(size=12, color='black'),
                    tickfont=dict(size=12, color='black'), row=3, col=1,  range=[samledf['surface_snow_thickness'].max()*0.7, samledf['surface_snow_thickness'].max()+(samledf['surface_snow_thickness'].max()*0.1)])

    # Legger til piler for vindretning
    for time, row in df_resampled.iterrows():
        radian = row['wind_from_direction'] * (pi / 180)
        fig.add_annotation(
            x=time,
            y=0,  # Sett en passende y-posisjon for pilene dine
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor='black',
            ax=20 * cos(radian),
            ay=20 * sin(radian),
            row=2, col=1  #  * -1 Plotly's koordinatsystem er invertert for y
        )

    for time, row in df_met_resampled.iterrows():
        radian = row['Wind Direction'] * (pi / 180)
        fig.add_annotation(
            x=time,
            y=0,  # Sett en passende y-posisjon for pilene dine
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor='black',
            ax=20 * cos(radian),
            ay=20 * sin(radian),
            row=2, col=1  #  * -1 Plotly's koordinatsystem er invertert for y
        )

  

    fig.update_yaxes(title_text='Temperatur', title_font=dict(size=12, color='black'),
                    tickfont=dict(size=12, color='black'),showgrid=True, row=1, col=1)


    fig.update_yaxes(title_text='Nedbør (mm)', title_font=dict(size=12, color=precipitation_color),
                    tickfont=dict(size=12, color=precipitation_color), row=1, col=1,showgrid=False , secondary_y=True, range=[0, 6])


    fig.update_yaxes(title_text='Vindhastighet (m/s)', title_font=dict(size=12, color=wind_color),
                    tickfont=dict(size=12, color=wind_color), row=2, col=1)



    fig.update_layout(
        title={
        'text': f"{navn} - {altitude} moh. - ID: {stasjonsid}",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    title_font=dict(
        family="Arial, sans-serif",
        size=24,
        color="black"
    ),width=900, 
    height=plotheight, 
    showlegend=False)

    return fig

def vindrose_stasjon(stasjonsid, dager_tidligere, navn, altitude):
    df = vindrose(stasjonsid, dager_tidligere)
    vind_hastighet = ['0-4 m/s', '4-8 m/s', '8-11 m/s', '11-14 m/s', '14-17 m/s', '17-20 m/s', '20-25 m/s', '>25 m/s']
    colors = ['#482878', '#3e4989', '#31688e', '#26828e', '#1f9e89', '#35b779', '#6ece58', '#b5de2b']
    direction_to_degrees = {
    'N': 0,
    'NØ': 45,
    'Ø': 90,
    'SØ': 135,
    'S': 180,
    'SV': 225,
    
    'V': 270,
    'NV': 315
    }
    theta = [direction_to_degrees[dir_bin] for dir_bin in df.index]

    fig = go.Figure()
    for i, hastighet in enumerate(vind_hastighet):
        fig.add_trace(go.Barpolar(
            r=df[hastighet].tolist(),
            theta=theta,
            name=hastighet,
            marker_color=colors[i],
        ))

    
    fig.update_traces(text=['Nord','N-Ø', 'Øst', 'S-Ø', 'Sør', 'S-V', 'Vest', 'N-V'])
    fig.update_layout(
        title=f"{navn} - {altitude} moh. - ID: {stasjonsid}",
        font_size=16,
        legend_font_size=16,
        polar_radialaxis_ticksuffix='%',
        polar_angularaxis_rotation=90,
        polar_angularaxis_direction='clockwise',

    )
    
    return fig