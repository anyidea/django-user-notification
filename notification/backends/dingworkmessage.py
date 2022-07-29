import typing

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from markdownify import markdownify

from notification.backends.base import BaseNotificationBackend, notify
from notification.models import Message, MessageTemplate


class DingTalkWorkMessageNotificationBackend(BaseNotificationBackend):
    """
    A backend handle dingtalk work message.
    For details, see: https://open.dingtalk.com/document/isvapp-server/asynchronous-sending-of-enterprise-session-messages
    """  # noqa

    id = "dingtalkworkmessage"
    message_subtype = "markdown"

    def __init__(self, *args, agent_id=None, app_key=None, app_secret=None, **kwargs):
        try:
            self.notification_settting = settings.DJANGO_USER_NOTIFICATION[self.id]
        except (AttributeError, KeyError):
            raise ImproperlyConfigured(
                "'DJANGO_USER_NOTIFICATION[{}]' must be "
                "set in settings.py".format(self.id)
            )

        try:
            self.agent_id = agent_id or self.notification_settting["agent_id"]
        except KeyError:
            raise ImproperlyConfigured(
                "'agent_id' must be set in "
                "settings.DJANGO_USER_NOTIFICATION[{}]".format(self.id)
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

    def render_template(self, template: MessageTemplate, context: dict) -> str:
        try:
            html_content = Template(template.content.html).render(Context(context))
            return markdownify(html_content)
        except Exception as e:
            raise ValueError("Render message failed: %s" % e)

    def make_content(
        self, title, content, recipients, recipient_field, **kwargs
    ) -> dict:
        return {
            "msgtype": self.message_subtype,
            self.msgtype: {"title": title, "text": content},
        }

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
        """
        url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2"
        params = {"access_token": self.get_access_token()}
        for recipient in recipients:
            dingtalk_userid = self.get_recipient(recipient, recipient_field)
            notify_kwargs = {"userid_list": dingtalk_userid}
            json = {
                "agent_id": self.agent_id,
                "msg": message.content,
                **notify_kwargs,
                **kwargs,
            }
            try:
                resp = requests.post(url, params=params, json=json)
                resp.raise_for_status()
                ret = resp.json()
                assert ret["errcode"] == 0, ret["errmsg"]
            except Exception as e:
                self.on_failure(message, recipient, e, save, notify_kwargs)
            else:
                self.on_success(message, recipient, save, notify_kwargs)


def notify_by_dingtalk_workmessage(
    recipients: list[User],
    userid_field: typing.Union[str, typing.Callable],
    title: str = None,
    message: str = None,
    context: dict = None,
    template_code: str = None,
    save: bool = False,
    **kwargs,
):
    """
    Shortcut for dingtalk work message notification
    """
    return notify(
        recipients,
        title=title,
        message=message,
        context=context,
        template_code=template_code,
        backends=(DingTalkWorkMessageNotificationBackend,),
        save=save,
        recipient_field=userid_field,
        message_kwargs={},
        **kwargs,
    )
