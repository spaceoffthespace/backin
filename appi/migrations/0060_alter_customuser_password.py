# Generated by Django 4.2.3 on 2023-08-04 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0059_task_commission_alter_customuser_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$1IszfZEsZi1yAWm4WBYsSr$voptEsEjD6Ca7iiiJk7TCCYAOhCLSeuvWYTggAnnuSc=', max_length=128),
        ),
    ]
