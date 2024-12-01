from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from .apidata.snowsense import hent_snowsense
#from .apidata.vaerplot import met_stasjon_supblot, met_stasjon_supblot_u_nedbor, vaerplot, met_plot, vindrose_stasjon, met_og_ein_stasjon_plot, frost_samledf
import json
from .models import Omrade, Stasjon, Klimapunkt, Webkamera, Sensor, Metogram
from .apidata.utils import utm_to_latlon, sjekk_element_ids
from .apidata.plotfunksjoner import plotfunksjon_stasjon, vindrose_stasjon, plotfunksjon_stasjon_ny, plotfunksjon_griddata
from .apidata.stasjon import hent_stasjonsinfo
from datetime import datetime, timedelta

import requests


# Create your views here.

def grid_plot_view(request, x, y):
    i_dag = datetime.now()
    startdato = i_dag - timedelta(days=10)
    startdato = startdato.strftime('%Y-%m-%d')
    sluttdato = i_dag + timedelta(days=7)
    sluttdato = sluttdato.strftime('%Y-%m-%d')
    print(startdato)
    #try:
    fig = plotfunksjon_griddata(x, y, startdato, sluttdato)
    print('fig klar i views')
    # Gjør figuren klar for HTML-visning
    plot_html = fig.to_html(full_html=False)

    return render(request, 'vaerdata/gridplot.html', {'plot_html': plot_html})

    #except requests.exceptions.RequestException as e:
        # Håndter API-feil
    #    return render(request, 'vaerdata/gridplot.html', {'error': f"Feil ved henting av API-data: {e}"})

def gridpunkt(request, x, y):
    i_dag = datetime.now()
    startdato = i_dag - timedelta(days=10)
    startdato = startdato.strftime('%Y-%m-%d')
    sluttdato = i_dag + timedelta(days=7)
    sluttdato = sluttdato.strftime('%Y-%m-%d')
    print(startdato)
    #try:
    fig = plotfunksjon_griddata(x, y, startdato, sluttdato)
    print('fig klar i views')
    # Gjør figuren klar for HTML-visning
    fig_json = json.loads(fig.to_json())
    return JsonResponse({
        'fig_json': fig_json
    })

@cache_page(60 * 15)
def stasjon_plot_view(request, stasjon_id):
    """
    Henter sensordata for en stasjon via et API og genererer riktig plott.
    
    Args:
        request: Django HTTP Request.
        stasjon_id: ID-en til stasjonen som skal plottes.
    
    Returns:
        Django HttpResponse med et plott som HTML.
    """

    # Eksempel: URL til eksternt API for å hente sensordata
    api_url_observations = f"https://frost.met.no/observations/availableTimeSeries/v0.jsonld?sources=SN{stasjon_id}&referencetime=2024-11-23"
    
    client_id = 'b8b1793b-27ff-4f4d-a081-fcbcc5065b53'
    client_secret = '7f24c0ca-ca82-4ed6-afcd-23e657c2e78c'
    
    try:
        # Hent data fra API
        response_observations = requests.get(api_url_observations,auth=(client_id,client_secret)) 
        response_observations.raise_for_status()
        json_data_observations = response_observations.json()  # Parse JSON-responsen


        
        # Liste over elementer vi ønsker å sjekke
        elements = [
            'air_temperature',
            'surface_snow_thickness',
            'wind_speed',
            'wind_from_direction',
            'sum(precipitation_amount PT10M)'
        ]
        
        # Finn hvilke elementer som er tilgjengelige
        tilgjengelige_elementer = sjekk_element_ids(json_data_observations, elements)
        print(f'tilgjengelige elementer: {tilgjengelige_elementer}')
        stasjonsdata = hent_stasjonsinfo(stasjon_id)
        # Sjekk hvilke typer sensorer vi skal inkludere
        percipitation = any('sum(precipitation_amount' in eid for eid in tilgjengelige_elementer)
        wind = any('wind_from_direction' in eid for eid in tilgjengelige_elementer)
        snow = any('surface_snow_thickness' in eid for eid in tilgjengelige_elementer)

        # Generer plottet basert på tilgjengelige sensorer
        fig = plotfunksjon_stasjon_ny(
            lat=stasjonsdata['coordinates'][1],  # Eksempelkoordinater - bruk verdier fra stasjonen din
            lon=stasjonsdata['coordinates'][0],
            navn=stasjonsdata['name'],
            altitude=stasjonsdata['masl'],
            stasjonsid=stasjon_id,
            elements=tilgjengelige_elementer,
            dager_etter_met=2,
            dager_tidligere_frost=5,
            percipitation=percipitation,
            wind=wind,
            snow=snow
        )

        # Gjør figuren klar for HTML-visning
        plot_html = fig.to_html(full_html=False)

        return render(request, 'vaerdata/stasjon_plot.html', {'plot_html': plot_html})

    except requests.exceptions.RequestException as e:
        # Håndter API-feil
        return render(request, 'vaerdata/stasjon_plot.html', {'error': f"Feil ved henting av API-data: {e}"})

#@cache_page(60 * 15)
def stasjon(request, stasjonid):
    stasjon = get_object_or_404(Stasjon, kode=stasjonid)
    client_id = 'b8b1793b-27ff-4f4d-a081-fcbcc5065b53'
    client_secret = '7f24c0ca-ca82-4ed6-afcd-23e657c2e78c'
    
    api_url_observations = f"https://frost.met.no/observations/availableTimeSeries/v0.jsonld?sources=SN{stasjonid}&referencetime=2024-11-23"
    # Hent data fra API
    response_observations = requests.get(api_url_observations,auth=(client_id,client_secret)) 
    response_observations.raise_for_status()
    json_data_observations = response_observations.json()  # Parse JSON-responsen


    
    # Liste over elementer vi ønsker å sjekke
    elements = [
        'air_temperature',
        'surface_snow_thickness',
        'wind_speed',
        'wind_from_direction',
        'sum(precipitation_amount PT10M)'
    ]
    
    # Finn hvilke elementer som er tilgjengelige
    tilgjengelige_elementer = sjekk_element_ids(json_data_observations, elements)
    stasjonsdata = hent_stasjonsinfo(stasjonid)
    # Sjekk hvilke typer sensorer vi skal inkludere
    percipitation = any('sum(precipitation_amount' in eid for eid in tilgjengelige_elementer)
    wind = any('wind_from_direction' in eid for eid in tilgjengelige_elementer)
    snow = any('surface_snow_thickness' in eid for eid in tilgjengelige_elementer)

    # Generer plottet basert på tilgjengelige sensorer
    fig = plotfunksjon_stasjon_ny(
        lat=stasjonsdata['coordinates'][1],  # Eksempelkoordinater - bruk verdier fra stasjonen din
        lon=stasjonsdata['coordinates'][0],
        navn=stasjonsdata['name'],
        altitude=stasjonsdata['masl'],
        stasjonsid=stasjonid,
        elements=tilgjengelige_elementer,
        dager_etter_met=2,
        dager_tidligere_frost=5,
        percipitation=percipitation,
        wind=wind,
        snow=snow
    )
    fig_json = json.loads(fig.to_json())
    return JsonResponse({
        'fig_json': fig_json
    })

#@cache_page(60 * 15)
def stasjon_gammel(request, stasjonid):
    '''Funksjonen er ikkje optimal, bør ha bedre logikk for å finne ut kva type stasjon det er.'''
    stasjon = get_object_or_404(Stasjon, kode=stasjonid)
    altitude = stasjon.altitude
    koordinater = stasjon.koordinater
    koordinater_split = koordinater.split(',')
    east = koordinater_split[0]
    north = koordinater_split[1]
    lat, lon = utm_to_latlon(east, north, 33, 'N')
    stasjonstype = stasjon.beskrivelse
    sensor_names = [sensor.name for sensor in stasjon.sensor_elements.all()]
 
    #sett antall dager tidligere for frost
    dager_tidligere_frost = 4
    dager_etter_met = 2
    
    if stasjonstype == 'snodybde':
        #print(f'stasjonstype: {stasjonstype}')
        #print(f'stasjon {stasjon.navn} er inne i if-statement')
        fig = plotfunksjon_stasjon(lat, lon, stasjon.navn, altitude, stasjonid, sensor_names, dager_etter_met, dager_tidligere_frost, wind=True, percipitation=True, snow=True)
        fig_json = json.loads(fig.to_json())
        return JsonResponse({
            'fig_json': fig_json
        })
    elif stasjonstype == 'nedbor':
        #print(f'stasjonstype: {stasjonstype}')
        #print(f'stasjon {stasjon.navn} er inne i if-statement')
        fig = plotfunksjon_stasjon(lat, lon, stasjon.navn, altitude, stasjonid, sensor_names, dager_etter_met, dager_tidligere_frost,percipitation=True)
        fig_json = json.loads(fig.to_json())
        return JsonResponse({
            'fig_json': fig_json
        })
    elif stasjonstype == 'vind':
        #print(f'stasjonstype: {stasjonstype}')
        #print(f'stasjon {stasjon.navn} er inne i if-statement')
        fig = plotfunksjon_stasjon(lat, lon, stasjon.navn, altitude, stasjonid, sensor_names, dager_etter_met, dager_tidligere_frost, wind=True)
        fig_json = json.loads(fig.to_json())
        return JsonResponse({
            'fig_json': fig_json
        })
    elif stasjonstype == 'sno':
        fig = plotfunksjon_stasjon(lat, lon, stasjon.navn, altitude, stasjonid, sensor_names, dager_etter_met, dager_tidligere_frost, wind=False, percipitation=True, snow=True)
        fig_json = json.loads(fig.to_json())
        return JsonResponse({
            'fig_json': fig_json
        })
    else:
        return JsonResponse({'message': 'Feil'})



#@cache_page(60 * 15)
def lokaltest(request, omrade):
    omrade = get_object_or_404(Omrade, navn=omrade)
    #print(omrade)
    metogrammer = omrade.metogrammer.all()
    webkameraer = omrade.webkameraer.all()
    stasjoner = omrade.stasjoner.all()
    vindroser = omrade.vindroser.all()
    klimapunkter = omrade.klimapunkter.all()
    for klimapunkt in klimapunkter:
        print(f'klimapunkt: {klimapunkt.koordinater}')
    #print(f'stasjoner  {stasjoner}')
    ploturls = []
    ploturls_vindrose = []
    ploturls_grid = []
    for stasjon in stasjoner:
        #print(f'stasjonskode: {stasjon.kode}')
        plot_url = reverse('stasjon', args=[stasjon.kode])  # Genererer URL basert på stasjonens kode
        ploturls.append(request.build_absolute_uri(plot_url))  # Legger til fullstendig URL inkludert domene
        ploturl_vind = reverse('vindrose_stasjon_data', args=[stasjon.kode])
        ploturls_vindrose.append(request.build_absolute_uri(ploturl_vind))
        #print(f'ploturls_vind: {ploturls__vindrose}')
    for klimapunkt in klimapunkter:
        x, y = klimapunkt.koordinater.split(", ")
        plot_url = reverse('gridpunkt', args=[x, y])
        ploturls_grid.append(request.build_absolute_uri(plot_url))
        print(f'ploturls_grid: {ploturls_grid}')
    return render(request, 'vaerdata/visning.html', {
        'metogrammer': metogrammer,
        'webkameraer': webkameraer,
        'ploturls': ploturls,
        'ploturls_vindrose' : ploturls_vindrose,
        'ploturls_grid': ploturls_grid,
    })

def lokalvarsling(request, omrade):
    omrade = get_object_or_404(Omrade, navn=omrade)
    stasjoner = omrade.stasjoner.all()
    
    klimapunkter = omrade.klimapunkter.all()
    webkameraer = omrade.webkameraer.all()
    return render(request, 'vaerdata/lokalvarsling.html', {
        'omrade': omrade,
        'stasjoner': stasjoner,
        'klimapunkter': klimapunkter,
        'webkameraer': webkameraer
    })

def index(request):
    yrsvg1 = 'https://www.yr.no/nb/innhold/1-2205713/meteogram.svg'  #Kvitenova
    yrsvg2 = 'https://www.yr.no/nb/innhold/1-169829/meteogram.svg'
    yrlink1 = 'https://www.yr.no/nb/detaljer/graf/1-2205713'
    yrlink2 =  'https://www.yr.no/nb/detaljer/graf/1-169829'
    webkamera1 = 'https://webkamera.atlas.vegvesen.no/public/kamera?id=1429008_1'

    return render(request, 'vaerdata/vaerdata.html', {
        'yrsvg1': yrsvg1,
        'yrsvg2': yrsvg2,
        'yrlink1': yrlink1,
        'yrlink2': yrlink2,
        'webkamera1': webkamera1})

def get_snowsense(request):
    snowsense_data = hent_snowsense()
    print(snowsense_data)
    #graph1 = vaerplot(værstasjoner[58705]['lat'], værstasjoner[58705]['lon'], navn=værstasjoner[58705]['navn'], altitude=værstasjoner[58705]['altitude'], stasjonsid=58705, elements=['air_temperature'])
    #graph2 = vaerplot(værstasjoner[58703]['lat'], værstasjoner[58703]['lon'], navn=værstasjoner[58703]['navn'], altitude=værstasjoner[58703]['altitude'], stasjonerid=58703, elements=['air_temperature', 'sum(precipitation_amount PT10M)', 'wind_speed'])
    return JsonResponse({
        'snowsense_data': snowsense_data
    })

   

def vindrose_stasjon_data(request, stasjonid):
    stasjon = get_object_or_404(Stasjon, kode=stasjonid)
    dager_tidligere = 1
    fig = vindrose_stasjon(stasjonid, dager_tidligere, stasjon.navn, stasjon.altitude)
    
    fig_json = json.loads(fig.to_json())

    return JsonResponse({
        'fig_json': fig_json
    })

