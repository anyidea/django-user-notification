import json
import typing

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_dysmsapi20170525.models import SendSmsRequest
from alibabacloud_tea_openapi import models as open_api_models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from notification.backends.base import BaseNotificationBackend, notify


class AliyunSMSNotificationBackend(BaseNotificationBackend):
    """
    A backend handle aliyun sms message.
    For details, see: https://help.aliyun.com/document_detail/419273.htm?spm=a2c4g.11186623.0.0.34375695hoVPSt
    """  # noqa

    id = "aliyunsms"
    message_subtype = "plain"
    endpoint = "dysmsapi.aliyuncs.com"

    def __init__(
        self, *args, access_key_id=None, access_key_secret=None, sign_name=None, **kwargs
    ):
        try:
            self.notification_settting = settings.DJANGO_USER_NOTIFICATION[self.id]
        except (AttributeError, KeyError):
            raise ImproperlyConfigured(
                "'DJANGO_USER_NOTIFICATION[{}]' must be set in settings.py".format(
                    self.id
                )
            )

        try:
            access_key_id = access_key_id or self.notification_settting["access_key_id"]
        except KeyError:
            raise ImproperlyConfigured(
                "'access_key_id' must be set "
                "in settings.DJANGO_USER_NOTIFICATION[{}]".format(self.id)
            )

        try:
            access_key_secret = (
                access_key_secret or self.notification_settting["access_key_secret"]
            )
        except KeyError:
            raise ImproperlyConfigured(
                "'access_key_secret' must be set "
                "in settings.DJANGO_USER_NOTIFICATION[{}]".format(self.id)
            )

        try:
            self.sign_name = sign_name or self.notification_settting["sign_name"]
        except KeyError:
            raise ImproperlyConfigured(
                "'sign_name' must be set "
                "in settings.DJANGO_USER_NOTIFICATION[{}]".format(self.id)
            )

        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=self.endpoint,
        )
        self.client = Dysmsapi20170525Client(config)
        super().__init__(*args, **kwargs)

    def make_content(self, title, content, receivers, recipient_field, **kwargs) -> dict:
        return {
            "sign_name": kwargs.get("sign_name") or self.sign_name,
            "template_code": kwargs["template_code"],
            "template_param": json.dumps(kwargs["template_param"]),
        }

    def perform_send(self, message, recipients, recipient_field, save, **kwargs):
        """
        For details, see: https://help.aliyun.com/document_detail/419273.htm?spm=a2c4g.11186623.0.0.34375695hoVPSt
        """  # noqa
        for recipient in recipients:
            phone = self.get_recipient(recipient, recipient_field)
            notify_kwargs = {"phone_numbers": str(phone)}
            try:
                request = SendSmsRequest(**notify_kwargs, **message.content)
                self.client.send_sms(request)
            except Exception as e:
                self.on_failure(message, recipient, e, save, notify_kwargs)
            else:
                self.on_success(message, recipient, save, notify_kwargs)


def notify_by_aliyun_sms(
    recipients: list[User],
    phone_field: typing.Union[str, typing.Callable],
    template_code: str,
    context: dict,
    sign_name: str = None,
    save=False,
    **kwargs,
):
    """
    Shortcut for aliyun sms message notification
    """
    message_kwargs = {
        "template_code": template_code,
        "template_param": context,
        "sign_name": sign_name,
    }

    return notify(
        recipients,
        backends=(AliyunSMSNotificationBackend,),
        save=save,
        recipient_field=phone_field,
        message_kwargs=message_kwargs,
        **kwargs,
    )
