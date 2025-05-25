from rest_framework import serializers
from .models import AccessLog, RadioClass

class AccessLogDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ['id', 'rfid_tag_attempted', 'is_access_granted']
        read_only_fields = ['id'] # ID только для чтения

class RadioClassStatusSerializer(serializers.Serializer):
    radio_class_id = serializers.IntegerField(required=True)  # ID радиокласса
    status = serializers.ChoiceField(  # Статус зарядки
        choices=RadioClass.STATUS_CHOICES,
        required=True
    )
