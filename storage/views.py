from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, AccessLog, StorageUnit
from django.utils import timezone

@csrf_exempt  # Отключаем CSRF для простоты (в реальном проекте нужно настроить правильно)
def rfid_access(request):
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


# Форма для тестирования RFID
def index(request):
    return render(request, "test_form.html")

# Просмотр журнала доступа
def access_log_view(request):
    access_logs = AccessLog.objects.all().order_by('-access_time')  # Получаем все записи из AccessLog и сортируем по времени в обратном порядке
    return render(request, 'access_log.html', {'access_logs': access_logs})
