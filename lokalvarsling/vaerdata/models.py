from django.db import models

class Omrade(models.Model):
    navn = models.CharField(max_length=100, unique=True)
    stasjoner = models.ManyToManyField('Stasjon', related_name='omrader', blank=True)  # Use 'omrader' here for reverse access'
    klimapunkter = models.ManyToManyField('Klimapunkt', related_name='omrader', blank=True)  # Use 'omrader' here for reverse access'
    webkameraer = models.ManyToManyField('Webkamera', related_name='omrader', blank=True)  # Use 'omrader' here for reverse access'
    metogrammer = models.ManyToManyField('Metogram', related_name='omrader', blank=True)  # Use 'omrader' here for reverse access'
    vindroser = models.ManyToManyField('Vindrose', related_name='omrader', blank=True)  # Use 'omrader' here for reverse access'
    
    def __str__(self):
        return self.navn

class Stasjon(models.Model):
    kode = models.CharField(max_length=50, unique=True)
    navn = models.CharField(max_length=100)
    beskrivelse = models.TextField(blank=True)
    koordinater = models.CharField(max_length=100, blank=True)
    altitude = models.IntegerField(null=True)
    sensor_elements = models.ManyToManyField('Sensor', blank=True)

    def __str__(self):
        return self.navn

class Klimapunkt(models.Model):
    navn = models.CharField(max_length=100)
    beskrivelse = models.TextField(blank=True)
    koordinater = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.navn

class Webkamera(models.Model):
    navn = models.CharField(max_length=100)
    beskrivelse = models.TextField(blank=True)
    koordinater = models.CharField(max_length=100, blank=True)
    url = models.TextField(blank=True)

    def __str__(self):
        return self.navn

class Sensor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Metogram(models.Model):
    navn = models.CharField(max_length=100)
    url = models.TextField(blank=True)

    def __str__(self):
        return self.navn
    
class Vindrose(models.Model):
    stasjon = models.ForeignKey(Stasjon, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.stasjon.navn}'