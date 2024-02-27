from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .apidata.snowsense import hent_snowsense
#from .apidata.vaerplot import met_stasjon_supblot, met_stasjon_supblot_u_nedbor, vaerplot, met_plot, vindrose_stasjon, met_og_ein_stasjon_plot, frost_samledf
import json
from .models import Omrade, Stasjon, Klimapunkt, Webkamera, Sensor, Metogram
from .apidata.utils import utm_to_latlon
from .apidata.plotfunksjoner import plotfunksjon_stasjon, vindrose_stasjon


# Create your views here.
def stasjon(request, stasjonid):
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



    else:
        return JsonResponse({'message': 'Feil'})




def lokaltest(request, omrade):
    omrade = get_object_or_404(Omrade, navn=omrade)
    #print(omrade)
    metogrammer = omrade.metogrammer.all()
    webkameraer = omrade.webkameraer.all()
    stasjoner = omrade.stasjoner.all()
    vindroser = omrade.vindroser.all()
    #print(f'stasjoner  {stasjoner}')
    ploturls = []
    ploturls__vindrose = []
    for stasjon in stasjoner:
        #print(f'stasjonskode: {stasjon.kode}')
        plot_url = reverse('stasjon', args=[stasjon.kode])  # Genererer URL basert på stasjonens kode
        ploturls.append(request.build_absolute_uri(plot_url))  # Legger til fullstendig URL inkludert domene
        ploturl_vind = reverse('vindrose_stasjon_data', args=[stasjon.kode])
        ploturls__vindrose.append(request.build_absolute_uri(ploturl_vind))
        #print(f'ploturls_vind: {ploturls__vindrose}')
    return render(request, 'vaerdata/visning.html', {
        'metogrammer': metogrammer,
        'webkameraer': webkameraer,
        'ploturls': ploturls,
        'ploturls__vindrose' : ploturls__vindrose,
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

