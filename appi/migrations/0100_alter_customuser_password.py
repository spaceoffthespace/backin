# Generated by Django 4.2.3 on 2023-12-25 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0099_customuser_allow_unaffordable_tasks_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$0JyVpf4LUsXcbzXHy2xkf3$HBNo3G60cNzwP5KwQRtnr7aKOjbLBCj/7SDK4rDEWko=', max_length=128),
        ),
    ]
