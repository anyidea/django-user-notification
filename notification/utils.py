from base64 import b64encode

from notification import backends
from notification.backends.base import BaseNotificationBackend


def make_etag(*args):
    """
    Generate custom etag
    """
    return "-".join(b64encode(tag.encode("utf-8")).decode("utf-8") for tag in args)


def get_group_name(user_id: int):
    return f"notify-{user_id}"


def get_notification_backend(msg_type: str):
    """
    Get notification backend.
    """
    for att in dir(backends):
        attr_value = (att, getattr(backends, att))
        if (
            attr_value is issubclass(BaseNotificationBackend, attr_value)
            and getattr(attr_value, "id") == msg_type
        ):
            return attr_value
    else:
        raise ValueError(f"Notification backend {msg_type} doesn't exist.")
