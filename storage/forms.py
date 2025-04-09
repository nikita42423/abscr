from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['rfid_tag', 'group', 'last_name', 'first_name', 'access']
        labels = {
            'rfid_tag': 'UID RFID',
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'group': 'Группа',
            'access': 'Разрешение доступа',
        }
        widgets = {
            'rfid_tag': forms.TextInput(attrs={'class': 'form-control', 'label' : 'UID RFID'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'access': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
