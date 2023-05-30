from base64 import b64encode


def make_etag(*args):
    """
    Generate custom etag
    """
    return "-".join(b64encode(tag.encode("utf-8")).decode("utf-8") for tag in args)


def get_group_name(user_id: int):
    return f"notify-{user_id}"


def get_notification_backend_class(msg_type):
    """
    Get notification backend.
    """
    from notification import backends
    from notification.base import BaseNotificationBackend

    for att in dir(backends):
        attr_value = (att, getattr(backends, att))
        if (
            attr_value is issubclass(BaseNotificationBackend, attr_value)
            and getattr(attr_value, "id") == msg_type
        ):
            return attr_value
    else:
        raise ValueError(f"Notification backend {msg_type} doesn't exist.")


def init_settings():
    from django.conf import settings

    settings.TINYMCE_DEFAULT_CONFIG = getattr(
        settings,
        "TINYMCE_DEFAULT_CONFIG",
        {
            "tinymce_version": "6",
            "height": 300,
            "width": 600,
            "menubar": True,
            "language": "en_US",
        },
    )
    settings.TINYMCE_JS_URL = getattr(settings, "TINYMCE_JS_URL", "https://cdn.jsdelivr.net/npm/tinymce/tinymce.min.js")
