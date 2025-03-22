from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('rfid_access/', views.rfid_access_view, name='rfid_access'),
    path('access_log/', views.access_log_view, name='access_log'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
