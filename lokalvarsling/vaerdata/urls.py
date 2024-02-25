from django.urls import path

from . import views

#TODO: Må få inn view for stasjonsplot, og så generere url for kvar stasjon, og iterere over dei i template?

urlpatterns = [
    path("", views.index, name="index"),
    path("lokaltest/<str:omrade>/", views.lokaltest, name="lokaltest"),
    path("lokalvarsling/<str:omrade>/", views.lokalvarsling, name="lokalvarsling"),
    path("stasjon/<int:stasjonid>/", views.stasjon, name="stasjon"),
    path("get_snowsense/", views.get_snowsense, name="get_snowsense"),
    path("get_graph1/", views.get_graph1, name="get_graph1"),
    path("vindrose_stasjon_data/", views.vindrose_stasjon_data, name="vindrose_stasjon_data"),
    path("met_frost_plot1/", views.met_frost_plot1, name="met_frost_plot1"),
]