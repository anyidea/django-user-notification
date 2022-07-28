from base64 import b64encode


def make_etag(*args):
    """
    Generate custom etag
    """
    return "-".join(b64encode(tag.encode("utf-8")).decode("utf-8") for tag in args)


def get_group_name(user_id: int):
    return f"notify-{user_id}"


def get_notification_backend(msg_type: str):
    """
    Get notification type
    """
    raise NotImplementedError
