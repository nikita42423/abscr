from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, AccessLog, StorageUnit
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout # Для авторизации
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AccessLogDataSerializer
from rest_framework import status

class rfid_access_view(APIView):
    def post(self, request):
        serializer = AccessLogDataSerializer(data=request.data)  # Используем serializer для проверки данных
        if serializer.is_valid():
            rfid_tag = serializer.validated_data['rfid_tag_attempted'] # Получаем RFID-метку из данных сериализатора
            try:
                storage_unit = StorageUnit.objects.get(pk=1)  # Для тестирования (ID блок хранения = 1)
                student = Student.objects.get(rfid_tag=rfid_tag)  # Студент найден

                is_access_granted = student.access  # Определяем, разрешен ли доступ

                #Создаем запись в лог
                AccessLog.objects.create(
                    student=student,
                    access_time=timezone.now(),
                    is_access_granted=is_access_granted,
                    storage_unit=storage_unit,
                    rfid_tag_attempted=rfid_tag  # Сохраняем rfid_tag
                )

                message = 'Доступ разрешен' if is_access_granted else 'Доступ запрещен: нет разрешения' # Тернарный оператор
                status_message = 'success' if is_access_granted else 'error'
                status_code = status.HTTP_200_OK if is_access_granted else status.HTTP_403_FORBIDDEN
                return Response({'status': status_message, 'message': message}, status=status_code) # success

            except Student.DoesNotExist:
                # Студент не найден

                #Создаем запись в лог
                AccessLog.objects.create(
                    student=None,
                    access_time=timezone.now(),
                    is_access_granted=False,
                    storage_unit=storage_unit,
                    rfid_tag_attempted=rfid_tag # Сохраняем rfid_tag
                )

                return Response({'status': 'error', 'message': 'Студент не найден'}, status=status.HTTP_404_NOT_FOUND) # not found
        else:
            return Response(serializer.errors, status_message=status.HTTP_400_BAD_REQUEST)  # invalid data

# Просмотр журнала доступа
@login_required
def access_log_view(request):
    access_logs = AccessLog.objects.all().order_by('-access_time')  # Получаем все записи из AccessLog и сортируем по времени в обратном порядке
    data = {
        'access_logs': access_logs,
        'activate_page': 'access_logs',
        }
    return render(request, 'pages/access_log.html', data)

# Просмотр студентов
@login_required
def students_view(request):
    students = Student.objects.all().order_by('group')  # Получаем все записи из AccessLog и сортируем по времени в обратном порядке
    data = {
        'students': students,
        'activate_page': 'students',
        }
    return render(request, 'pages/students.html', data)

# Авторизация
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'pages/login.html', {'error': 'Неверные учетные данные'})
    else:
        return render(request, 'pages/login.html')

# Логаут
def logout_view(request):
    logout(request)
    return redirect('login')

# Форма для тестирования RFID
@login_required
def home_view(request):
        return render(request, 'pages/test_form.html')

# Изменение доступа студентов
csrf_exempt  # Отключаем CSRF для этого представления (используем токен в заголовке)
def update_access(request, student_id):
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=student_id)

            access_value = request.POST.get('access') == 'true'  # Преобразуем строку в boolean
            print(f"Student ID: {student_id}, Access: {access_value}")  # Логируем данные

            student.access = access_value
            student.save()
            return JsonResponse({'success': True})
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Студент не найден'})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})
