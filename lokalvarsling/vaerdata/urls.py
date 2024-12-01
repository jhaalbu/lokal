from django.urls import path

from . import views

#TODO: Må få inn view for stasjonsplot, og så generere url for kvar stasjon, og iterere over dei i template?

urlpatterns = [
    path("", views.index, name="index"),
    path("enkelstasjon/<int:stasjon_id>/", views.stasjon_plot_view, name="stasjon_plot_view"),
    path("<str:omrade>/", views.lokaltest, name="lokaltest"),
    path("lokalvarsling/<str:omrade>/", views.lokalvarsling, name="lokalvarsling"),
    path("stasjon/<int:stasjonid>/", views.stasjon, name="stasjon"),
    path("gridpunkt/<int:x>/<int:y>/", views.gridpunkt, name="gridpunkt"),
    path("vindrose/<int:stasjonid>", views.vindrose_stasjon_data, name="vindrose_stasjon_data"),
    path("griddata/<int:x>/<int:y>", views.grid_plot_view, name="grid_plot_view"),

]