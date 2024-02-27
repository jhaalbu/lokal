import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import pi, cos, sin
from metno_locationforecast import Place, Forecast
from .met import metno_forecast_to_dataframe
from .stasjon import frost_api, vindrose, bearbeid_frost, frost_samledf

user_agent = "Stedspesifikk v/0.1 jan.helge.aalbu@vegvesen.no"


def plotfunksjon_stasjon(lat, lon, navn, altitude, stasjonsid, elements, dager_etter_met, dager_tidligere_frost, percipitation=False, wind=False, snow=False, ):   
    # Henter data fra YR for ein gitt koordinat
    vaer = Place(navn, lat, lon, altitude)
    vaer_forecast = Forecast(vaer, user_agent)
    vaer_forecast.update()

    # Bearbeider nedhenta data fra yr og lager df for enkel plotting

    met_df = metno_forecast_to_dataframe(vaer_forecast, dager_etter_met)

    df_met_resampled = met_df.resample('3H').mean()
    

    # Henter data fra frost for ein gitt stasjon

    df = frost_api(stasjonsid, dager_tidligere_frost, elements, timeoffsets='PT0H')
    df_bearbeida = bearbeid_frost(df)
    samledf = frost_samledf(df_bearbeida)
    
    # Bearbeiding av data for å få tilpassa plott, vindpiler..
    df_resampled = samledf.resample('3H').mean()

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