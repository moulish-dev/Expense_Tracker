# Generated by Django 5.1 on 2024-08-21 23:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense_tracker_app', '0002_transaction_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='merchant',
            field=models.CharField(default='merchant', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='scheduled_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='scheduled_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('completed', 'Completed'), ('scheduled', 'Scheduled')], default='completed', max_length=9),
        ),
        migrations.AddField(
            model_name='transaction',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
