# Generated by Django 4.2.3 on 2023-07-23 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0018_alter_customuser_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$iE6ukr29aMBj9zDg7saKhh$ogb2Y9f8qLhwizat22qsp3AzlPORt25uTDsbDVsIb7A=', max_length=128),
        ),
    ]
