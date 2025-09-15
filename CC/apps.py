from django.apps import AppConfig


class CcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CC'

    def ready(self):
        import CC.signals
