from django.urls import path

from . import views

app_name = "cipherlab"

urlpatterns = [
    path("algorithms/", views.algorithm_catalog, name="algorithms"),
    path("operate/", views.operate, name="operate"),
    path("history/", views.history, name="history"),
]