# Generated by Django 4.2.3 on 2023-09-06 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appi', '0077_customuser_last_login_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_task_completion_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tasks_done_today',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default='pbkdf2_sha256$600000$nAUXzFBhlG5pg7DWKh5iyE$f47Y1/6jGJYj5aYVSD9UFbLItO0aXjc9sLuTVM0bnhQ=', max_length=128),
        ),
    ]
