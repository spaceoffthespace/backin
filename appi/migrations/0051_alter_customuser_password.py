# Generated by Django 4.2.3 on 2023-07-28 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0050_alter_customuser_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$Fsg8kwVZrGiafdLkdtlQn7$XwKPQSelela5ddttSYSBN35fgf9uFecyMJk3RXtIyVE=', max_length=128),
        ),
    ]
