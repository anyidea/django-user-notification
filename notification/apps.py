from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notification"

    def ready(self):
        from . import app_settings as defaults
        from django.conf import settings
        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
