from django.db import models

class Group(models.Model):
    group_name = models.CharField(max_length=255)

    def __str__(self):
        return self.group_name

class Student(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, related_name='students')
    rfid_tag = models.CharField(max_length=255, unique=True)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    access = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Radioclass(models.Model):
    serial_number = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('charged', 'Заряжен'),
        ('charging', 'Заряжается'),
        ('unplugged', 'Не подключен'),
    ]
    status = models.CharField(max_length=20, default='Не подключен', choices=STATUS_CHOICES)  # Статус зарядки
    last_updated = models.DateTimeField(auto_now=True)  # Время последнего обновления

    def __str__(self):
        return f"{self.model} ({self.serial_number})"

class StorageUnit(models.Model):
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return self.location_name

class StorageSlot(models.Model):
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.IntegerField()
    radioclass = models.ForeignKey(Radioclass, on_delete=models.SET_NULL, blank=True, null=True, related_name='slots')
    STATUS_CHOICES = [
        ('available', 'Доступно'),
        ('occupied', 'Занято'),
        ('unavailable', 'Недоступно'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
    )

    def __str__(self):
        return f"{self.storage_unit} - Slot {self.slot_number}"


class AccessLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True, related_name='access_logs')
    access_time = models.DateTimeField()
    is_access_granted = models.BooleanField(default=False)
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE)
    slot = models.ForeignKey(StorageSlot, on_delete=models.SET_NULL, blank=True, null=True)
    radioclass = models.ForeignKey(Radioclass, on_delete=models.SET_NULL, blank=True, null=True)
    rfid_tag_attempted = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Access attempt by {self.student} at {self.access_time}"
