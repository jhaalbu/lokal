from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .apidata.snowsense import hent_snowsense
from .apidata.vaerplot import met_stasjon_supblot, met_stasjon_supblot_u_nedbor, vaerplot, met_plot, vindrose_stasjon, met_og_ein_stasjon_plot, frost_samledf
import json
from .models import Omrade, Stasjon, Klimapunkt, Webkamera, Sensor, Metogram
from .apidata.utils import utm_to_latlon

værstasjoner = {
    58705: {'eigar': 'SVV', 
            'navn':'Rv15 Strynefjell - Kvitenova', 
            'lat': 61.988, 'lon': 7.330, 
            'altitude': 1422, 
            'elements': [
                'air_temperature', 
                'wind_from_direction', 
                'wind_speed']},
    58703: {'eigar': 'SVV', 
            'navn':'Rv15 Skjerdingsdalen', 
            'lat':61.9633, 'lon': 7.254, 
            'altitude': 590,
            'elements': [
                'air_temperature', 
                'sum(precipitation_amount PT10M)', 
                'wind_speed',
                'wind_from_direction',
                'surface_snow_thickness',
                ]},
    15951: {'eigar': 'SVV', 
            'navn':'Rv15 Breidalen II', 
            'lat': 62.0103, 'lon': 7.392, 
            'altitude': 929,
            'elements': [
                'air_temperature', 
                'sum(precipitation_amount PT10M)', 
                'wind_speed',
                'wind_from_direction',
                'surface_snow_thickness',
                ]},
}

andre_stasjoner = {
    'Stavbrekka': {'stasjonstype':'Snowsense', 'lat':62.0176, 'lon':7.375, 'altitude':1300}
}
# Create your views here.
def stasjon(request, stasjonid):
    stasjon = get_object_or_404(Stasjon, kode=stasjonid)
    altitude = stasjon.altitude
    koordinater = stasjon.koordinater
    koordinater_split = koordinater.split(',')
    east = koordinater_split[0]
    north = koordinater_split[1]
    lat, lon = utm_to_latlon(east, north, 33, 'N')
    stasjonstype = stasjon.beskrivelse
    sensor_names = [sensor.name for sensor in stasjon.sensor_elements.all()]
    print(f'stasjonstype: {stasjonstype}')
    if stasjonstype == 'snodybde' or stasjonstype == 'nedbor':
        print(f'stasjon {stasjon.navn} er inne i if-statement')
        fig = met_stasjon_supblot(lat, lon, stasjon.navn, altitude, stasjonid, sensor_names)
        fig_json = json.loads(fig.to_json())
        return JsonResponse({
            'fig_json': fig_json
        })
    if stasjonstype == 'vind':
        fig = met_stasjon_supblot_u_nedbor(lat, lon, stasjon.navn, altitude, stasjonid, sensor_names)
        fig_json = json.loads(fig.to_json())
        return JsonResponse({
            'fig_json': fig_json
        })

    # Utfør ytterligere logikk eller retur her...

    # Eksempel på retur av en JsonResponse
    else:
        return JsonResponse({'message': 'Feil'})


def stasjonsplot(request, stasjonid):
    #TODO: tanken her er vel å lage ein view som genererer ein plot for kvar stasjon, og så generere url for kvar stasjon, og iterere over dei i template?
    fig = met_stasjon_supblot(værstasjoner[58703]['lat'], værstasjoner[58703]['lon'], værstasjoner[58703]['navn'], værstasjoner[58703]['altitude'], 58703, værstasjoner[58703]['elements'])
    fig_json = json.loads(fig.to_json())
    return JsonResponse({
        'fig_json': fig_json
    })
    

def lokaltest(request, omrade):
    omrade = get_object_or_404(Omrade, navn=omrade)
    print(omrade)
    metogrammer = omrade.metogrammer.all()
    webkameraer = omrade.webkameraer.all()
    stasjoner = omrade.stasjoner.all()
    print(f'stasjoner  {stasjoner}')
    ploturls = []
    for stasjon in stasjoner:
        print(f'stasjonskode: {stasjon.kode}')
        plot_url = reverse('stasjon', args=[stasjon.kode])  # Genererer URL basert på stasjonens kode
        ploturls.append(request.build_absolute_uri(plot_url))  # Legger til fullstendig URL inkludert domene
    print(f'ploturls: {ploturls}')
    return render(request, 'vaerdata/visning.html', {
        'metogrammer': metogrammer,
        'webkameraer': webkameraer,
        'ploturls': ploturls,
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

def vaer(request):
    vaerplot_graf = vaerplot(værstasjoner[58703]['lat'], værstasjoner[58703]['lon'], værstasjoner[58703]['navn'], værstasjoner[58703]['altitude'], 58703, værstasjoner[58703]['elements'])
    return JsonResponse({
        'vaerplot_graf': vaerplot_graf
    })

def get_graph1(request):
    fig = met_plot(værstasjoner[58703]['lat'], værstasjoner[58703]['lon'], navn=værstasjoner[58703]['navn'], altitude=værstasjoner[58703]['altitude'])
    
    fig_json = json.loads(fig.to_json())

    return JsonResponse({
        'fig_json': fig_json
    })

def met_frost_plot1(request):
    fig = met_stasjon_supblot(værstasjoner[58703]['lat'], værstasjoner[58703]['lon'], værstasjoner[58703]['navn'], værstasjoner[58703]['altitude'], 58703, værstasjoner[58703]['elements'])
    fig_json = json.loads(fig.to_json())
    return JsonResponse({
        'fig_json': fig_json
    })
    

def vindrose_stasjon_data(request):
    fig = vindrose_stasjon(58705, dager_tidligere=1)
    
    fig_json = json.loads(fig.to_json())

    return JsonResponse({
        'fig_json': fig_json
    })

