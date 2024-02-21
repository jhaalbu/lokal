import plotly.graph_objects as go
import plotly.io as pio
import plotly.utils as pu
from metno_locationforecast import Place, Forecast
from .met import metno_temperatur, metno_nedbør
from .stasjon import frost_api, vindrose, bearbeid_frost, frost_samledf
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
import numpy as np
import pandas as pd

user_agent = "Stedspesifikk v/0.1 jan.helge.aalbu@vegvesen.no"

def vaerplot(lat, lon, navn, altitude, stasjonsid, elements):
    dager_tidligere = 4
    user_agent = "Stedspesifikk v/0.1 jan.helge.aalbu@vegvesen.no"
    vaer = Place(navn, lat, lon, altitude)
    vaer_forecast = Forecast(vaer, user_agent)
    vaer_forecast.update()
    time_nebør, nedbør = metno_nedbør(vaer_forecast, dager_tidligere)

    time_temperatur, temperatur = metno_temperatur(vaer_forecast, dager_tidligere)

    nedbør_cumsum = np.cumsum(nedbør).tolist()

    line_elements = ['air_temperature', 'wind_speed']
    bar_elements = ['sum(precipitation_amount PT10M)']


    # Lager til figuren
    fig = go.Figure()

    #Plotter ut data fra yr apiet
    fig.add_trace(go.Bar(x=time_nebør, y=nedbør, name='Nedbør (YR)', width=1000 * 3600 * 5, yaxis='y2'))
    fig.add_trace(go.Scatter(x=time_temperatur, y=temperatur, mode='lines', name='temperatur (YR)'))
    fig.add_trace(go.Scatter(x=time_nebør, y=nedbør_cumsum, mode='lines', name='Kumulativ nedbør (YR)', fill='tozeroy', fillcolor='rgba(0, 0, 255, 0.1)', yaxis='y3'))
    
    #Henter ut data fra forst apiet
    værhist = hent_frost(stasjonsid, dager_tidligere, elements, timeoffsets='PT0H')

    for element in værhist:
        if element == 'sum(precipitation_amount PT10M)':
            fig.add_trace(go.Bar(x=værhist[element]['referenceTime'], y=værhist[element]['value'], name='Nedbør (YR)', width=1000 * 3600 * 1, yaxis='y2'))
        else:
            fig.add_trace(go.Scatter(x=værhist[element]['referenceTime'], y=værhist[element]['value'], mode='lines', name=element))
    #fig.add_trace(go.Bar(x=time_nebør, y=nedbør, name='nedbør', width=1000 * 3600 * 5))
    #fig.add_trace(go.Scatter(x=df['referenceTime'], y=df['value'], mode='lines', name='Temperatur (værstasjon)'))

    fig.update_layout(
        yaxis=dict(
            title='Temperatur',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            )
        ),
        yaxis2=dict(
            title='Nedbør',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            title='Kumulativ nedbør',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        ),
    )
    fig_json = json.loads(fig.to_json())
    # Convert the graph to JSON format
    return json.dumps(fig_json, safe=False)

def met_plot(lat, lon, navn, altitude, dager=4):
    user_agent = "Stedspesifikk v/0.1 jan.helge.aalbu@vegvesen.no"
    vaer = Place(navn, lat, lon, altitude)
    vaer_forecast = Forecast(vaer, user_agent)
    vaer_forecast.update()
    time_nebør, nedbør = metno_nedbør(vaer_forecast, dager)

    time_temperatur, temperatur = metno_temperatur(vaer_forecast, dager)

    nedbør_cumsum = np.cumsum(nedbør).tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=time_nebør, y=nedbør, name='Nedbør (YR)', width=1000 * 3600 * 5, yaxis='y2'))
    fig.add_trace(go.Scatter(x=time_temperatur, y=temperatur, mode='lines', name='temperatur (YR)'))
    fig.add_trace(go.Scatter(x=time_nebør, y=nedbør_cumsum, mode='lines', name='Kumulativ nedbør (YR)', fill='tozeroy', fillcolor='rgba(0, 0, 255, 0.1)', yaxis='y3'))
    fig.update_layout(
        yaxis=dict(
            title='Temperatur',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            )
        ),
        yaxis2=dict(
            title='Nedbør',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            title='Kumulativ nedbør',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        ),
    )
    
    return fig
 

def frostplot_temp_nedbør_snø(stasjonsid, dager, elements):
    traces = []
    max_snødybde = 0
    for element in elements:
        print(element)
        #print(traces)
        if element == 'sum(precipitation_amount PT10M)':
            print('Inne i nedbør')
            tid, verdi = hent_frost(stasjonsid, dager, element, timeoffsets='PT0H')
            trace = {
            'x': tid,
            'y': verdi,
            'type': 'bar',
            'name': 'Nedbør',
            'marker': {'color': 'blue'},
            'width': 1000 * 3600 * 5,
            'yaxis': 'y2'
            }
            traces.append(trace)
        elif element == 'air_temperature':
            print('Inne i temperatur')
            tid, verdi = hent_frost(stasjonsid, dager, element, timeoffsets='PT0H')
            trace = {
            'x': tid,
            'y': verdi,
            'type': 'scatter',
            'name': 'Temperatur',
            'marker': {'color': 'red'},
            'yaxis': 'y'
            }
            traces.append(trace)
        elif element == 'surface_snow_thickness':
            print('Inne i snødybde')
            tid, verdi = hent_frost(stasjonsid, dager, element, timeoffsets='PT0H')
            trace = {
            'x': tid,
            'y': verdi,
            'type': 'scatter',
            'name': 'Snødybde',
            'marker': {'color': 'blue'},
            'fill': 'tozeroy',
            'fillcolor': 'rgba(0, 0, 255, 0.1)', 
            'yaxis': 'y3'
            }
            traces.append(trace)

            max_snødybde = max((v for v in verdi if v is not None), default=None)
    layout = {
        'yaxis2': {
            'title': 'Nedbør',
            'overlaying': 'y',
            'side': 'right',
            'showgrid': False,
            'position': 0.85,  # Hide the grid lines
        },
        'yaxis': {
            'title': 'Temperatur',
            'showgrid': False,  # Hide the grid lines
        },
        'yaxis3': {  # Add a second y-axis
            'title': 'Snødybde',
            'overlaying': 'y',
            'side': 'right',
            'showgrid': False,  # Hide the grid lines
            'zeroline': False,  # Hide the zero line
            'position': 0.90,
            'range': [0.3*max_snødybde, max_snødybde+0.3*max_snødybde] 
        },
        'xaxis': {'domain': [0.0, 0.8]},
    }
    return {'data' : traces, 'layout': layout}

def frostplot_vind(stasjonsid, dager, elements):
    traces = []

    for element in elements:
        print(element)
        #print(traces)
        if element == 'wind_from_direction':
            print('Inne i wind_from_direction')
            tid, verdi = hent_frost(stasjonsid, dager, element, timeoffsets='PT0H')
            trace = {
            'x': tid,
            'y': verdi,
            'type': 'scatter',
            'name': 'Vindretning',
            'marker': {'color': 'blue'},
            'yaxis': 'y'
            }
            traces.append(trace)
        elif element == 'wind_speed':
            print('Inne i wind_speed')
            tid, verdi = hent_frost(stasjonsid, dager, element, timeoffsets='PT0H')
            trace = {
            'x': tid,
            'y': verdi,
            'type': 'scatter',
            'name': 'Vindhastighet',
            'marker': {'color': 'red'},
            'yaxis': 'y2'
            }
            traces.append(trace)

    layout = {
        'yaxis': {
            'title': 'Vindretning',
            'showgrid': False,

        },
        'yaxis2': {
            'title': 'Vindestyrke',
            'side': 'right',
            'showgrid': False,  # Hide the grid lines
            'overlaying': 'y'
        },

    }
    return {'data' : traces, 'layout': layout}
    # return {'data' : traces}

def vindrose_stasjon(stasjonsid, dager_tidligere):
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
    print(theta)
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
        title='Vindrose for siste døgn, stasjon ' + str(stasjonsid),
        font_size=16,
        legend_font_size=16,
        polar_radialaxis_ticksuffix='%',
        polar_angularaxis_rotation=90,
        polar_angularaxis_direction='clockwise',

    )
    
    return fig

# def met_og_ein_stasjon_plot(lat, lon, navn, altitude, stasjonsid, elements,  dager_etter_met=2, dager_tidligere_frost=2):   
#     vaer = Place(navn, lat, lon, altitude)
#     vaer_forecast = Forecast(vaer, user_agent)
#     vaer_forecast.update()
#     time_nebør, nedbør = metno_nedbør(vaer_forecast, dager_etter_met)
#     nedbør_cumsum = np.cumsum(nedbør).tolist()
#     time_temperatur, met_temperatur = metno_temperatur(vaer_forecast, dager_etter_met)


#     df_temp = frost_api(stasjonsid, dager_tidligere_frost, elements, timeoffsets='PT0H')
#     samledf = frost_samledf(df_temp)
#     print('samledf')
#     print(samledf)

#     fig = go.Figure()
#     fig.add_trace(go.Bar(x=time_nebør, y=nedbør, name='Nedbør (YR)', width=1000 * 3600 * 5, yaxis='y2'))
#     fig.add_trace(go.Scatter(x=time_temperatur, y=met_temperatur, mode='lines', name='temperatur (YR)'))
#     fig.add_trace(go.Scatter(x=time_nebør, y=nedbør_cumsum, mode='lines', name='Kumulativ nedbør (YR)', fill='tozeroy', fillcolor='rgba(0, 0, 255, 0.1)', yaxis='y3'))
    
#     navndict = {
#         'air_temperature': 'Temperatur',
#          'wind_speed': 'Vindhastighet', 
#          'sum(precipitation_amount PT10M)': 'Nedbør', 
#          'wind_from_direction': 'Vindretning',
#          'surface_snow_thickness': 'Snødybde'
#          }
    
#     fig.add_trace(go.Bar(x=samledf.index, y=samledf['sum(precipitation_amount PT10M)'], name='Nedbør', width=1000 * 3600 * 1, yaxis='y2'))
    
#     fig.add_trace(go.Scatter(x=samledf.index, y=samledf['air_temperature'], name='Temperatur', mode='lines'))
#     fig.add_trace(go.Scatter(x=samledf.index, y=samledf['wind_speed'], name='Vindhastighet', mode='lines'))

#     fig.update_layout(
#         yaxis=dict(
#             title='Temperatur',
#             titlefont=dict(
#                 color='rgb(148, 103, 189)'
#             ),
#             tickfont=dict(
#                 color='rgb(148, 103, 189)'
#             )
#         ),
#         yaxis2=dict(
#             title='Nedbør',
#             titlefont=dict(
#                 color='rgb(148, 103, 189)'
#             ),
#             tickfont=dict(
#                 color='rgb(148, 103, 189)'
#             ),
#             overlaying='y',
#             side='right'
#         ),
#         yaxis3=dict(
#             title='Kumulativ nedbør',
#             titlefont=dict(
#                 color='rgb(148, 103, 189)'
#             ),
#             tickfont=dict(
#                 color='rgb(148, 103, 189)'
#             ),
#             overlaying='y',
#             side='right'
#         ),
#     )
#     return fig
    

def met_og_ein_stasjon_plot(lat, lon, navn, altitude, stasjonsid, elements, dager_etter_met=2, dager_tidligere_frost=2):   
    vaer = Place(navn, lat, lon, altitude)
    vaer_forecast = Forecast(vaer, user_agent)
    vaer_forecast.update()
    time_nebør, nedbør = metno_nedbør(vaer_forecast, dager_etter_met)
    nedbør_cumsum = np.cumsum(nedbør).tolist()
    time_temperatur, met_temperatur = metno_temperatur(vaer_forecast, dager_etter_met)

    df = frost_api(stasjonsid, dager_tidligere_frost, elements, timeoffsets='PT0H')
    df_bearbeida = bearbeid_frost(df)
    samledf = frost_samledf(df_bearbeida)

    # Define a color palette
    temperature_color = 'rgba(255, 165, 0, 0.8)'  # orange
    precipitation_color = 'rgba(0, 123, 255, 0.8)'  # blue
    wind_color = 'rgba(40, 167, 69, 0.8)'  # green

    # Create the figure
    fig = go.Figure()

    # Plotting precipitation from YR
    fig.add_trace(go.Bar(x=time_nebør, y=nedbør, name='Nedbør (YR)', width=1000 * 3600,
                         yaxis='y2', marker_color=precipitation_color))

    # Plotting temperature from YR
    fig.add_trace(go.Scatter(x=time_temperatur, y=met_temperatur, mode='lines',
                             name='temperatur (YR)', line=dict(color=temperature_color)))

    # Plotting cumulative precipitation from YR
    fig.add_trace(go.Scatter(x=time_nebør, y=nedbør_cumsum, mode='lines+markers',
                             name='Kumulativ nedbør (YR)', fill='tozeroy', 
                             fillcolor='rgba(0, 0, 255, 0.1)', yaxis='y3'))

    # Plotting other data from the samledf DataFrame
    fig.add_trace(go.Bar(x=samledf.index, y=samledf['sum(precipitation_amount PT10M)'],
                         name='Nedbør', width=1000 * 3600, yaxis='y2', marker_color=precipitation_color))

    fig.add_trace(go.Scatter(x=samledf.index, y=samledf['air_temperature'], name='Temperatur',
                             mode='lines', line=dict(color=temperature_color)))

    fig.add_trace(go.Scatter(x=samledf.index, y=samledf['wind_speed'], name='Vindhastighet',
                             mode='lines', line=dict(color=wind_color)))

    # Update the layout to incorporate the design principles
    fig.update_layout(
        title='Stasjonsdata mot YR-data',
        yaxis=dict(
            title='Temperatur',
            titlefont=dict(size=14, color=temperature_color),
            tickfont=dict(size=12, color=temperature_color)
        ),
        yaxis2=dict(
            title='Nedbør',
            titlefont=dict(size=14, color=precipitation_color),
            tickfont=dict(size=12, color=precipitation_color),
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            title='Kumulativ nedbør',
            titlefont=dict(size=14, color='rgba(0, 0, 255, 0.8)'),
            tickfont=dict(size=12, color='rgba(0, 0, 255, 0.8)'),
            overlaying='y',
            side='right',
            showgrid=False  # Hide gridlines for this axis
        ),
        legend=dict(x=0.1, y=1.1, orientation='h'),
        margin=dict(l=100, r=100, t=100, b=100),  # Adjust margins to fit legend and title
        font=dict(family='Arial, sans-serif'),
        paper_bgcolor='white',  # Set background color to white for contrast
        plot_bgcolor='white'    # Set plot background color to white
    )

    # Add annotations if necessary
    # e.g., fig.add_annotation(x=..., y=..., text='Annotation', showarrow=True, arrowhead=1)

    return fig
