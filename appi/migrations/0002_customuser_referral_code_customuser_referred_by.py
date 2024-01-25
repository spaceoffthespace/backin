# Generated by Django 4.2.3 on 2023-07-09 15:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='referral_code',
            field=models.CharField(default=5213521, max_length=30, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
