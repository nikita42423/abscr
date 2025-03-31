from rest_framework import serializers
from .models import AccessLog

class AccessLogDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ['id', 'rfid_tag_attempted', 'is_access_granted']
        read_only_fields = ['id'] # id только для чтения
