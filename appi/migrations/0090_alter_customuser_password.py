# Generated by Django 4.2.3 on 2023-10-17 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0089_alter_customuser_password_alter_task_task_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$39PWAf33XePfeyzPIn6kos$LnRi0BxJKwH6DpzkXsT1ZfRRc3CH13wSY4WJx8EI3kg=', max_length=128),
        ),
    ]
