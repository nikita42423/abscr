from rest_framework import serializers
from .models import AccessLog, Radioclass

class AccessLogDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ['id', 'rfid_tag_attempted', 'is_access_granted']
        read_only_fields = ['id'] # ID только для чтения

class RadioclassStatusSerializer(serializers.Serializer):
    radio_class_id = serializers.IntegerField(required=True)  # ID радиокласса
    status = serializers.ChoiceField(  # Статус зарядки
        choices=Radioclass.STATUS_CHOICES,
        required=True
    )
