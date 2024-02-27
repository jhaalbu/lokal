from django.urls import path

from . import views

#TODO: Må få inn view for stasjonsplot, og så generere url for kvar stasjon, og iterere over dei i template?

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:omrade>/", views.lokaltest, name="lokaltest"),
    path("lokalvarsling/<str:omrade>/", views.lokalvarsling, name="lokalvarsling"),
    path("stasjon/<int:stasjonid>/", views.stasjon, name="stasjon"),
    path("vindrose/<int:stasjonid>", views.vindrose_stasjon_data, name="vindrose_stasjon_data"),

]