# Generated by Django 5.1.6 on 2025-03-15 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='is_guimc_member',
        ),
    ]
