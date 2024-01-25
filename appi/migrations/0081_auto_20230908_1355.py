from django.db import migrations

def migrate_account_types(apps, schema_editor):
    CustomUser = apps.get_model('appi', 'CustomUser')
    for user in CustomUser.objects.all():
        if user.account_type == 'standard':
            user.account_type = 'bronze'
        elif user.account_type == 'premium':
            user.account_type = 'silver'
        elif user.account_type == 'elite':
            user.account_type = 'gold'
        user.save()

class Migration(migrations.Migration):

    dependencies = [
    ('appi', '0080_alter_customuser_account_type_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_account_types),
    ]
