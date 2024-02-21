from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get_snowsense/", views.get_snowsense, name="get_snowsense"),
    path("get_graph1/", views.get_graph1, name="get_graph1"),
    path("vindrose_stasjon_data/", views.vindrose_stasjon_data, name="vindrose_stasjon_data"),
    path("met_frost_plot1/", views.met_frost_plot1, name="met_frost_plot1"),
]