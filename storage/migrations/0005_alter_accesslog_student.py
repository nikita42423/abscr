# Generated by Django 5.1.6 on 2025-03-15 17:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0004_accesslog_rfid_tag_attempted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesslog',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='access_logs', to='storage.student'),
        ),
    ]
