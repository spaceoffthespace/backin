# Generated by Django 4.2.3 on 2023-07-25 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0025_alter_customuser_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$hOnPWamI9H5RUFjxAsR9TU$BYbPdQ7491U4+MzJzu0KoqstDJdWQtQ7ibZpjXO1mtY=', max_length=128),
        ),
    ]
