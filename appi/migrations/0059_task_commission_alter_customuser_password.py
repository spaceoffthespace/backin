# Generated by Django 4.2.3 on 2023-08-01 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0058_alter_customuser_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='commission',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$3ReCd27ktjGDrXc1gLXcDx$wOjT+K3j3L8ntUWXFo+U5fFLDdmTwfWwdW/bbNaJ6hY=', max_length=128),
        ),
    ]
