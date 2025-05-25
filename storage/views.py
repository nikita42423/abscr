from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models.functions import TruncDay

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import AccessLogDataSerializer, RadioClassStatusSerializer
from .forms import StudentForm
from .models import Student, AccessLog, StorageUnit, RadioClass

import json


class rfid_access_view(APIView):
    """
    Класс API-эндпоинта для обработки доступа по RFID.

    Этот класс принимает RFID-метку, проверяет наличие студента в базе данных и его права доступа.
    В зависимости от результата проверки создается запись в журнале доступа (AccessLog).

    Методы:
        - POST: Принимает RFID-метку, проверяет доступ и создает запись в журнале.

    Возвращаемые статусы:
        - 200 OK: Успешная обработка запроса.
        - 400 Bad Request: Ошибка валидации данных.
    """
    def post(self, request):
        serializer = AccessLogDataSerializer(data=request.data)  # Валидация данных

        if serializer.is_valid():
            uid = serializer.validated_data['rfid_tag_attempted']  # Получаем RFID-метку из данных
            try:
                storage_unit = StorageUnit.objects.get(pk=1)  # Для тестирования (ID блок хранения = 1)
                student = Student.objects.get(rfid_tag=uid)  # Находим студента
                is_access_granted = student.access  # Проверяем доступ

                #Создаем запись в лог
                AccessLog.objects.create(
                    student=student,
                    access_time=timezone.now(),
                    is_access_granted=is_access_granted,
                    storage_unit=storage_unit,
                    rfid_tag_attempted=uid
                )

                # Возвращаем ответ
                message = 'Доступ разрешен' if is_access_granted else 'Доступ запрещен: нет разрешения'
                status_message = 'success' if is_access_granted else 'error'
                return Response({'status': status_message, 'message': message}, status=status.HTTP_200_OK)

            except Student.DoesNotExist:
                # студент не найден
                AccessLog.objects.create(
                    student=None,
                    access_time=timezone.now(),
                    is_access_granted=False,
                    storage_unit=storage_unit,
                    rfid_tag_attempted=uid
                )
                return Response({'status': 'error', 'message': 'Студент не найден'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status_message=status.HTTP_400_BAD_REQUEST)  # Ошибка валидации данных


@login_required  # Декоратор, который требует аутентификации пользователя
def access_log_view(request):
    """
    Представление для отображения журнала доступа.

    Этот метод извлекает все записи из модели AccessLog, сортирует их по времени доступа
    и возвращает их в шаблон с поддержкой пагинации (10 записей на странице).

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        Render: Возвращает отрендеренный шаблон с данными журнала доступа.
    """
    access_logs_list = AccessLog.objects.all().order_by('-access_time')  # Получаем все записи из модели AccessLog и сортируем их по времени доступа в обратном порядке
    page = request.GET.get('page', 1)  # Получаем номер страницы из параметров запроса (по умолчанию 1)
    paginator = Paginator(access_logs_list, 10)  # Создаем объект Paginator для реализации пагинации (10 записей на странице)

    try:
        access_logs = paginator.page(page)  # Получаем записи для указанной страницы
    except PageNotAnInteger:
        access_logs = paginator.page(1)  # Если номер страницы не является целым числом, возвращаем первую страницу
    except EmptyPage:
        access_logs = paginator.page(paginator.num_pages)  # Если номер страницы превышает количество доступных страниц, возвращаем последнюю страницу

    data = {
        'access_logs': access_logs,  # Записи журнала доступа для текущей страницы
        'activate_page': 'access_logs',  # Флаг для активации вкладки "Журнал доступа" в шаблоне
        }
    return render(request, 'pages/access_log.html', data)


@login_required  # Декоратор, который требует аутентификации пользователя
def students_view(request):
    """
    Представление для отображения списка студентов.

    Этот метод извлекает все записи из модели Student, сортирует их по группе
    и возвращает их в шаблон для отображения.

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        Render: Возвращает отрендеренный шаблон с данными о студентах.
    """
    # Получаем все записи из модели Student и сортируем их по группе
    students = Student.objects.all().order_by('group')

    data = {
        'students': students,  # Список студентов для отображения
        'activate_page': 'students',  # Флаг для активации вкладки "Студенты" в шаблоне
        }
    return render(request, 'pages/students.html', data)


def add_student(request):
    """
    Представление для добавления нового студента.

    Если запрос POST, обрабатывает форму добавления студента:
    - Если форма валидна, сохраняет данные и перенаправляет на страницу со списком студентов.
    - Если форма невалидна, отображает форму с ошибками.
    Если запрос GET, отображает пустую форму для добавления студента.

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        Render: Возвращает отрендеренный шаблон с формой добавления студента.
        Redirect: Перенаправляет на страницу со списком студентов в случае успешного сохранения.
    """
    # Проверяем метод запроса
    if request.method == 'POST':
        form = StudentForm(request.POST)  # Создаем экземпляр формы с данными из POST-запроса

        # Проверяем валидность формы
        if form.is_valid():
            form.save()  # Сохраняем данные формы в базе данных
            return redirect('students')  # Перенаправляем на страницу со списком студентов
    else:
        form = StudentForm()  # Создаем экземпляр пустой формы (для GET-запроса)

    return render(request, 'pages/add_student.html', {'form': form})


def upd_student(request, student_id):
    """
    Представление для изменения данных студента.

    Получает ID студента из параметров маршрута и загружает соответствующую запись.
    Если запрос POST, обрабатывает форму изменения студента:
    - Если форма валидна, сохраняет изменения и перенаправляет на страницу со списком студентов.
    - Если форма невалидна, отображает форму с ошибками.
    Если запрос GET, отображает форму с текущими данными студента.

    Args:
        request (HttpRequest): Объект запроса.
        student_id (int): ID студента, данные которого нужно изменить.

    Returns:
        Render: Возвращает отрендеренный шаблон с формой изменения студента.
        Redirect: Перенаправляет на страницу со списком студентов в случае успешного сохранения.
    """
    student = get_object_or_404(Student, pk=student_id)  # Получаем студента по ID или возвращаем ошибку 404, если студент не найден

    # Проверяем метод запроса
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student) # Создаем экземпляр формы с данными из POST-запроса и текущими данными студента

        # Проверяем валидность формы
        if form.is_valid():
            form.save()  # Сохраняем изменения в базе данных
            return redirect('students')  # Перенаправляем на страницу со списком студентов
    else:
        form = StudentForm(instance=student)  # Создаем экземпляр формы с текущими данными студента (для GET-запроса)

    return render(request, 'pages/upd_student.html', {'form': form, 'student': student})


def del_student(request, student_id):
    """
    Представление для удаления студента.

    Получает ID студента из параметров маршрута и загружает соответствующую запись.
    Если запрос POST, удаляет студента из базы данных и перенаправляет на страницу со списком студентов.
    Если запрос GET, отображает страницу с подтверждением удаления.

    Args:
        request (HttpRequest): Объект запроса.
        student_id (int): ID студента, которого нужно удалить.

    Returns:
        Render: Возвращает отрендеренный шаблон с подтверждением удаления.
        Redirect: Перенаправляет на страницу со списком студентов после удаления.
    """
    student = get_object_or_404(Student, pk=student_id)  # Получаем студента по ID или возвращаем ошибку 404, если студент не найден

    # Проверяем метод запроса
    if request.method == 'POST':
        student.delete()  # Удаляем студента из базы данных
        return redirect('students')  # Перенаправляем на страницу со списком студентов

    return render(request, 'pages/del_student.html', {'student': student})  # Возвращаем шаблон с подтверждением удаления


def login_view(request):
    """
    Представление для авторизации пользователя.

    Обрабатывает POST-запрос с учетными данными (имя пользователя и пароль).
    Если данные корректны, авторизует пользователя и перенаправляет на страницу журнала доступа.
    Если данные некорректны, отображает ошибку на странице входа.

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        Render: Возвращает страницу входа с сообщением об ошибке (если данные некорректны).
        Redirect: Перенаправляет на страницу журнала доступа в случае успешной авторизации.
    """
    # Проверяем метод запроса
    if request.method == 'POST':
        # Получаем имя пользователя и пароль из POST-запроса
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)  # Пробуем аутентифицировать пользователя

        # Если пользователь найден, авторизуем его и перенаправляем на страницу журнала доступа
        if user is not None:
            login(request, user)
            return redirect('access_log')
        else:
            # Если пользователь не найден, возвращаем страницу входа с сообщением об ошибке
            return render(request, 'pages/login.html', {'error': 'Неверные учетные данные'})
    else:
        # Возвращаем страницу входа (для GET-запроса)
        return render(request, 'pages/login.html')


def logout_view(request):
    """
    Представление для выхода пользователя из системы.

    Обрабатывает запрос на выход и перенаправляет пользователя на страницу входа.

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        Redirect: Перенаправляет на страницу входа.
    """
    logout(request)  # Выполняем выход пользователя из системы
    return redirect('login')  # Перенаправляем на страницу входа

# Изменение доступа студентов
def update_access(request, student_id):
    """
    Представление для изменения доступа студента.

    Обрабатывает POST-запрос с данными о доступе студента.
    Если студент найден, обновляет его статус доступа и возвращает успешный ответ.
    Если студент не найден или метод запроса некорректен, возвращает ответ с ошибкой.

    Args:
        request (HttpRequest): Объект запроса.
        student_id (int): ID студента, доступ которого нужно изменить.

    Returns:
        JsonResponse: Возвращает JSON-ответ с результатом операции.
    """
    # Проверяем метод запроса
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=student_id)  # Получаем студента по ID

            # Получаем данные из тела запроса и извлекаем значение доступа
            data = json.loads(request.body)
            access_value = data.get('access')

             # Обновляем статус доступа студента
            student.access = access_value
            student.save()

            # Возвращаем успешный ответ
            return JsonResponse({'success': True})
        except Student.DoesNotExist:
            # Если студент не найден, возвращаем ответ с ошибкой
            return JsonResponse({'success': False, 'error': 'Студент не найден'})

    # Если метод запроса некорректен, возвращаем ответ с ошибкой
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

class RadioClassStatusView(APIView):
    """
    Класс API-эндпоинта для обновления статуса радиокласса.

    Этот класс принимает POST-запрос с данными о радиоклассе и его новом статусе.
    Если данные корректны и радиокласс найден в базе данных, его статус обновляется.

    Методы:
        - POST: Обновляет статус радиокласса.

    Возвращаемые статусы:
        - 200 OK: Статус успешно обновлен.
        - 400 Bad Request: Ошибка валидации данных.
        - 404 Not Found: Радиокласс не найден.
    """
    def post(self, request):
        serializer = RadioClassStatusSerializer(data=request.data)  # Валидация данных

        # Проверка валидности данных
        if serializer.is_valid():
            # Получаем ID радиокласса и новый статус из данных
            radio_class_id = serializer.validated_data['radio_class_id']
            new_status = serializer.validated_data['status']

            try:
                radio_class = RadioClass.objects.get(id=radio_class_id)  # Поиск радиокласса в базе данных по ID

                # Обновление статуса радиокласса
                radio_class.status = new_status
                radio_class.last_updated = timezone.now()
                radio_class.save()

                # Возвращаем успешный ответ
                return Response(
                    {'status': 'success', 'message': 'Статус обновлен'},
                    status=status.HTTP_200_OK
                )
            except RadioClass.DoesNotExist:
                # Если радиокласс не найден, возвращаем ошибку 404
                return Response(
                    {'status': 'error', 'message': 'Радиокласс не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Если данные не валидны, возвращаем ошибку 400
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Отображение статуса радиокласса
@login_required  # Декоратор, который требует аутентификации пользователя
def radioclass_status_view(request):
    radioclass = RadioClass.objects.first()  # Пока что один радиокласс
    data = {
        'radioclass': radioclass,
    }
    return render(request, 'pages/radioclass_status.html', data)

# Статистика
@login_required  # Декоратор, который требует аутентификации пользователя
def radioclass_statistics_view(request):
    # Общее количество выданных радиоклассов
    total_issued = AccessLog.objects.count()

    # Количество свободных радиоклассов
    free_radio_classes = RadioClass.objects.exclude(accesslog__isnull=False).count()

    # Количество разрешенных и запрещенных доступов
    granted_access = AccessLog.objects.filter(is_access_granted=True).count()
    denied_access = AccessLog.objects.filter(is_access_granted=False).count()

    # Данные для графика
    issued_per_day = (
        AccessLog.objects
        .filter(access_time__gte=timezone.now() - timezone.timedelta(days=90))
        .annotate(day=TruncDay('access_time'))  # Группируем по дню
        .values('day')  # Получаем только поле 'day'
        .annotate(count=Count('id'))  # Считаем количество записей за день
        .order_by('day')
    )

    # Преобразуем QuerySet в список словарей
    issued_per_day_list = list(issued_per_day)

    # Преобразуем объекты datetime в строки
    for item in issued_per_day_list:
        item['day'] = item['day'].isoformat()

    # Преобразуем данные в JSON-строку с двойными кавычками
    issued_per_day_json = json.dumps(issued_per_day_list)

    data = {
        'total_issued': total_issued,
        'free_radio_classes': free_radio_classes,
        'granted_access': granted_access,
        'denied_access': denied_access,
        'issued_per_day': issued_per_day_json,
    }

    return render(request, 'pages/radioclass_statistics.html', data)
