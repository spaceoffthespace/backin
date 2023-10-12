# Generated by Django 4.2.3 on 2023-07-14 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0011_customuser_deliveryaddress_alter_customuser_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='pending_tasks',
            field=models.ManyToManyField(related_name='pending_users', to='appi.task'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$GBbO3ZYra60WV5azDr25eB$dZtoUfJOgHu7LbJO921rIFu71uD74eTOoMB/oxzxtBI=', max_length=128),
        ),
    ]
