
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
    print(tidspunkt_temp)
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


