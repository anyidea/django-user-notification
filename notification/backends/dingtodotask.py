import typing

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from notification.base import BaseNotificationBackend, notify
from notification.models import Message


class DingTalkToDoTaskNotificationBackend(BaseNotificationBackend):
    """
    A backend handle dingtalk todo message.
    https://open.dingtalk.com/document/orgapp-server/add-dingtalk-to-do-task
    """

    id = "dingtalktodotask"
    message_subtype = "plain"

    def __init__(self, *args, app_key=None, app_secret=None, **kwargs):
        try:
            self.notification_settting = settings.DJANGO_USER_NOTIFICATION[self.id]
        except (AttributeError, KeyError):
            raise ImproperlyConfigured(
                "'DJANGO_USER_NOTIFICATION[{}]' must be "
                "set in settings.py".format(self.id)
            )

        try:
            self.app_key = app_key or self.notification_settting["app_key"]
        except KeyError:
            raise ImproperlyConfigured(
                "'app_key' must be set in "
                "settings.DJANGO_USER_NOTIFICATION[{}]".format(self.id)
            )

        try:
            self.app_secret = app_secret or self.notification_settting["app_secret"]
        except KeyError:
            raise ImproperlyConfigured(
                "'app_secret' must be set in "
                "settings.DJANGO_USER_NOTIFICATION[{}]".format(self.id)
            )

        super().__init__(*args, **kwargs)

    def make_content(
        self, title, content, recipients, recipient_field, **kwargs
    ) -> dict:
        return {"subject": title, "description": content, **kwargs}

    def get_access_token(self):
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        resp = requests.get(url, params=params)
        ret = resp.json()
        return ret["access_token"]

    def perform_send(
        self, message: Message, recipients, recipient_field, save, **kwargs
    ) -> None:
        """
        Send dingtalk work message
        For details, see: https://open.dingtalk.com/document/isvapp-server/asynchronous-sending-of-enterprise-session-messages
        """  # noqa
        url = "https://api.dingtalk.com/v1.0/todo/users/{unionid}/tasks"
        headers = {"x-acs-dingtalk-access-token": self.get_access_token()}
        for recipient in recipients:
            dingtalk_unionid = self.get_recipient(recipient, recipient_field)
            notify_kwargs = {
                "unionid": dingtalk_unionid,
                "executorIds": [dingtalk_unionid],
            }
            url = url.format(unionid=dingtalk_unionid)
            json = {"executorIds": [dingtalk_unionid], **message.content}
            try:
                resp = requests.post(url, headers=headers, json=json)
                ret = resp.json()
                assert resp.status_code == 200, ret["message"]
            except Exception as e:
                self.on_failure(message, recipient, e, save, notify_kwargs)
            else:
                self.on_success(message, recipient, save, notify_kwargs)


def notify_by_dingtalk_todotask(
    recipients: list[User],
    unioinid_field: typing.Union[str, typing.Callable],
    title: str = None,
    message: str = None,
    context: dict = None,
    template_code: str = None,
    participant_ids: list[str] = None,
    due_time: int = None,
    priority: int = None,
    save: bool = False,
    **kwargs,
):
    """
    Shortcut for dingtalk todo tasks notification
    """
    message_kwargs = {
        "participantIds": participant_ids,
        "dueTime": due_time,
        "priority": priority,
        "notifyConfigs": {"dingNotify": "1"},
    }

    return notify(
        recipients,
        title=title,
        message=message,
        context=context,
        template_code=template_code,
        backends=(DingTalkToDoTaskNotificationBackend,),  # noqa
        save=save,
        recipient_field=unioinid_field,
        message_kwargs=message_kwargs,
        **kwargs,
    )
