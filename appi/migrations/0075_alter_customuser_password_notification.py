# Generated by Django 4.2.3 on 2023-08-23 11:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0074_customuser_last_address_update_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$v5YnTDpoTfKq0smRoKmCji$vnBrBemsXrGLzwTIf75wE4qrQQzCF14zmzaTlCAUhi4=', max_length=128),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('info', 'Information'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')], default='info', max_length=10)),
                ('title', models.CharField(max_length=150)),
                ('content', models.TextField()),
                ('link', models.URLField(blank=True, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
