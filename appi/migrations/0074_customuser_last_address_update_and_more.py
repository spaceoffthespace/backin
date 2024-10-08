# Generated by Django 4.2.3 on 2023-08-23 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0073_alter_customuser_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_address_update',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$ZcDLkCG6p9V4Ip6OJgIQPm$BAYJ5gpTKyTOzxivfx9b2Ftf72VQOwXvEnUiTalWAEs=', max_length=128),
        ),
    ]
