from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, AccessLog, StorageUnit
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout # Для авторизации
from django.contrib.auth.decorators import login_required

@csrf_exempt  # Отключаем CSRF для простоты (в реальном проекте нужно настроить правильно)
@login_required
def rfid_access_view(request):
    if request.method == 'POST':
        rfid_tag = request.POST.get('rfid_tag')
        try:
            storage_unit = StorageUnit.objects.get(pk=1) # Для тестирования (ID блок хранения = 1)
            student = Student.objects.get(rfid_tag=rfid_tag)
            # Студент найден, разрешаем доступ
            AccessLog.objects.create(
                student=student,
                access_time=timezone.now(),
                is_access_granted=True,
                storage_unit=storage_unit,
                slot=None,
                radioclass=None,
                rfid_tag_attempted=rfid_tag
            )
            return JsonResponse({'status': 'success', 'message': 'Доступ разрешен'})
        except Student.DoesNotExist:
            # Студент не найден, запрещаем доступ
            AccessLog.objects.create(
                student=None,  # Студент не идентифицирован
                access_time=timezone.now(),
                is_access_granted=False,
                storage_unit=storage_unit,
                slot=None,
                radioclass=None,
                rfid_tag_attempted=rfid_tag
            )
            return JsonResponse({'status': 'error', 'message': 'Доступ запрещен'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})

# Просмотр журнала доступа
@login_required
def access_log_view(request):
    access_logs = AccessLog.objects.all().order_by('-access_time')  # Получаем все записи из AccessLog и сортируем по времени в обратном порядке
    return render(request, 'access_log.html', {'access_logs': access_logs})

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
            return render(request, 'login.html', {'error': 'Неверные учетные данные'})
    else:
        return render(request, 'login.html')

# Логаут
def logout_view(request):
    logout(request)
    return redirect('login')

# Форма для тестирования RFID
@login_required
def home_view(request):
        return render(request, 'test_form.html')
