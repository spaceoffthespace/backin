# Generated by Django 4.2.3 on 2023-07-23 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0019_alter_customuser_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$zFH8lDUU4pPg8ueMQr6UtM$PBsGXbxQNHI+Ts2Az3ZhW0prKvrhW8HDxQuqh3WTx0E=', max_length=128),
        ),
    ]
