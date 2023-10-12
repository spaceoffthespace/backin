from django.apps import AppConfig


class AppiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appi'


class ProfilesConfig(AppConfig):
    name = 'appi'

    def ready(self):
        import profiles.signals