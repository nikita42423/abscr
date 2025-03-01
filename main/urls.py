from django.urls import path
from . import views


urlpatterns = [
	path('', views.index),
	# path('html_page', views.html_page),
	# path('image', views.image_view),
]
