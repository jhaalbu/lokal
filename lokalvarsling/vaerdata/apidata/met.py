
from datetime import datetime, timedelta

def metno_temperatur(metno_forecst, dager=3):
    tidspunkt_temp = []
    temperatur = []
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    tid = now + timedelta(dager)
    print(tid)
    for i in metno_forecst.data.intervals:
        if i.start_time <= tid:
            try:
                temperatur.append(i.variables['air_temperature'].value)
                tidspunkt_temp.append(i.start_time)
            except:
                continue
    return tidspunkt_temp, temperatur

def metno_nedbør(metno_forecst, dager=3):
    tidspunkt_nedbor = []
    nedbor = []
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    tid = now + timedelta(dager)
    for i in metno_forecst.data.intervals:
        if i.start_time <= tid:
            try:
                nedbor.append(i.variables['precipitation_amount'].value)
                tidspunkt_nedbor.append(i.start_time)
            except:
                continue
    return tidspunkt_nedbor, nedbor

def metno_vind(metno_forecst, dager=3):
    tidspunkt_vind = []
    vind = []
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    tid = now + timedelta(dager)
    for i in metno_forecst.data.intervals:
        if i.start_time <= tid:
            try:
                vind.append(i.variables['wind_speed'].value)
                tidspunkt_vind.append(i.start_time)
            except:
                continue
    return tidspunkt_vind, vind

def metno_vindretning(metno_forecst, dager=3):
    tidspunkt_vindretning = []
    vindretning = []
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    tid = now + timedelta(dager)
    for i in metno_forecst.data.intervals:
        if i.start_time <= tid:
            try:
                vindretning.append(i.variables['wind_from_direction'].value)
                tidspunkt_vindretning.append(i.start_time)
            except:
                continue
    return tidspunkt_vindretning, vindretning