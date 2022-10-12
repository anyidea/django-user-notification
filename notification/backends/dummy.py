from django.contrib.auth.models import User

from notification.base import BaseNotificationBackend, notify
from notification.models import Message


class DummyNotificationBackend(BaseNotificationBackend):
    """
    A backend handle dummy message.
    """

    id = "dummy"

    def make_content(self, title, content, recipients, recipient_field, **kwargs):
        return content

    def perform_send(
        self, message: Message, recipients, recipient_field, save, **kwargs
    ) -> None:
        """
        Send dummy message
        """
        for recipient in recipients:
            self.on_success(message, recipient, save)


def notify_by_dummy(
    recipients: list[User],
    title: str = None,
    message: str = None,
    context: dict = None,
    template_code: str = None,
    save: bool = False,
    mark: dict = None,
    **kwargs,
):
    """
    Shortcut for dummy notification
    """
    return notify(
        recipients,
        title=title,
        message=message,
        context=context,
        template_code=template_code,
        backends=(DummyNotificationBackend,),
        save=save,
        message_kwargs={},
        mark=mark,
        **kwargs,
    )
