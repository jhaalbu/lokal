from django.contrib import admin

# Register your models here.
from .models import Omrade, Stasjon, Klimapunkt, Webkamera, Sensor, Metogram, Vindrose

admin.site.register(Omrade)
admin.site.register(Stasjon)
admin.site.register(Klimapunkt)
admin.site.register(Webkamera)
admin.site.register(Sensor)
admin.site.register(Metogram)
admin.site.register(Vindrose)