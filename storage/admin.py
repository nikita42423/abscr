from django.contrib import admin
from .models import Student, RadioClass, StorageUnit, StorageSlot, AccessLog, Group


admin.site.register(Student)
admin.site.register(RadioClass)
admin.site.register(StorageUnit)
admin.site.register(StorageSlot)
admin.site.register(AccessLog)
admin.site.register(Group)
