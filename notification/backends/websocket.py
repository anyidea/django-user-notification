from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from notification.base import BaseNotificationBackend, notify
from notification.models import Message
from notification.utils import get_group_name

try:
    import channels.layers
except ImportError:
    pass


class WebsocketNotificationBackend(BaseNotificationBackend):
    """
    A backend handle websocket message.

    """

    id = "websocket"
    message_subtype = "plain"

    def make_content(
        self,
        title: str,
        content: str,
        recipients,
        recipient_field,
        msgtype="notify",
        **kwargs,
    ):
        return {
            "type": f"{msgtype}.message",
            "msgtype": msgtype,
            "title": title,
            "message": content,
            **kwargs,
        }

    def perform_send(
        self,
        message: Message,
        recipients: list[User],
        recipient_field,
        save,
        **kwargs,
    ):
        """
        For details, see: https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
        """
        channel_layer = channels.layers.get_channel_layer()
        for recipient in recipients:
            notify_kwargs = {"group_name": get_group_name(recipient.pk)}
            try:
                async_to_sync(channel_layer.group_send)(
                    notify_kwargs["group_name"], message.content
                )
            except Exception as e:
                self.on_failure(message, recipient, e, save, notify_kwargs)
            else:
                self.on_success(message, recipient, save, notify_kwargs)


def notify_by_websocket(
    recipients: list[User],
    title: str = None,
    message: str = None,
    context: dict = None,
    template_code: str = None,
    msgtype="notify",
    save: bool = False,
    **kwargs,
):
    """
    Shortcut for websocket notification
    """
    message_kwargs = {"msgtype": msgtype}

    return notify(
        recipients,
        title=title,
        message=message,
        context=context,
        template_code=template_code,
        backends=(WebsocketNotificationBackend,),
        save=save,
        message_kwargs=message_kwargs,
        **kwargs,
    )
