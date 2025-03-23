from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("analisis/", views.analisis, name="analisis"),
    path("tramo/<str:tramo_name>/", views.tramo_detail, name="tramo_detail"),
]