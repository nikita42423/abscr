from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('rfid_access/', views.rfid_access, name='rfid_access'),
    path('access_log/', views.access_log_view, name='access_log'),
]
