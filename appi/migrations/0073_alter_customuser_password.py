# Generated by Django 4.2.3 on 2023-08-15 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0072_alter_customuser_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$0zYxgOkGuAlWGI9X64o462$uG8jKBroEh7h+a51HufmFDYVQfNBQymhHLMpapYHxdI=', max_length=128),
        ),
    ]
