from django.urls import path
from . import views

urlpatterns = [
    path('', views.access_log_view, name='access_log'),
    path('rfid-access/', views.rfid_access_view.as_view(), name='rfid_access'),
    path('access-log/', views.access_log_view, name='access_log'),
    path('students/', views.students_view, name='students'),
    path('add-student/', views.add_student, name='add_student'),
    path('upd-student/<int:student_id>/', views.upd_student, name='upd_student'),
    path('del-student/<int:student_id>/', views.del_student, name='del_student'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('update-access/<int:student_id>/', views.update_access, name='update_access'),
]
