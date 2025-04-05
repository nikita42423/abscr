from django.urls import path
from . import views

urlpatterns = [
    path('rfid_access/', views.rfid_access_view.as_view(), name='rfid_access'),
    path('access_log/', views.access_log_view, name='access_log'),
    path('students/', views.students_view, name='students'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('update-access/<int:student_id>/', views.update_access, name='update_access'),
]
