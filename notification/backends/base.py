import logging
import typing

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Template
from django.utils.module_loading import import_string

from notification.models import Message, MessageTemplate, Notification

logger = logging.getLogger(__name__)


class BaseNotificationBackend:
    id = None
    message_subtype = "plain"
    message_class = Message
    notification_class = Notification

    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        self.fail_silently = fail_silently

    def on_failure(self, message, recipient, exc, save=False, notify_kwargs=None):
        if not self.fail_silently:
            raise exc

        logger.error(
            "Failed to send message to recipient: %s, error: %s",
            recipient,
            exc,
        )
        if save:
            if message.pk is None:
                message.save()

            if recipient is None:
                return

            self.notification_class.objects.create(
                to=recipient,
                message=message,
                notify_kwargs=notify_kwargs,
                is_sent=False,
            )

    def on_success(self, message, recipient, save=False, notify_kwargs=None):
        logger.info("Successfully send message to recipient: %s", recipient)
        if save:
            if message.pk is None:
                message.save()

            if recipient is None:
                return

            self.notification_class.objects.create(
                to=recipient,
                message=message,
                notify_kwargs=notify_kwargs,
                is_sent=True,
            )

    def render_template(self, template: MessageTemplate, context: dict) -> str:
        try:
            return Template(template.content.plain).render(Context(context))
        except Exception as e:
            raise ValueError("Render message failed: %s" % e)

    def make_content(
        self, title, content, recipients, recipient_field, **kwargs
    ) -> dict:
        raise NotImplementedError

    def get_recipient(
        self,
        recipient: list[User],
        recipient_field: typing.Union[str, typing.Callable],
    ) -> typing.Iterable[str]:
        if callable(recipient_field):
            return recipient_field(recipient)
        else:
            return getattr(recipient, recipient_field)

    def perform_send(self, message, recipients, recipient_field, save, **kwargs) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        """
        Clear notification
        """
        self.notification_class.objects.filter(message__msg_type=self.id).delete()
        self.message_class.objects.filter(msg_type=self.id).delete()

    def send_with_template(
        self,
        recipients: list[User],
        template: MessageTemplate,
        context: dict,
        title: str = None,
        mark: str = None,
        save: bool = False,
        recipient_field: typing.Union[str, typing.Callable] = None,
        message_kwargs: dict = None,
        **kwargs,
    ) -> None:
        """
        Send notification to receivers with template
        """
        rendered_content = self.render_template(template, context)
        message_kwargs = message_kwargs or {}
        if template.message_kwargs:
            message_kwargs = template.message_kwargs.update(message_kwargs)

        title = title or template.title
        message_content = self.make_content(
            title, rendered_content, recipients, recipient_field, **message_kwargs
        )
        message = self.message_class(
            title=title,
            content=message_content,
            template=template,
            render_kwargs=context,
            mark=mark,
            msg_type=self.id,
        )
        self.perform_send(message, recipients, recipient_field, save=save, **kwargs)

    def send(
        self,
        title: str,
        recipients: list[User],
        content: str,
        mark: str = None,
        save: bool = False,
        recipient_field: typing.Union[str, typing.Callable] = None,
        message_kwargs: dict = None,
        **kwargs,
    ) -> None:
        """
        Send notification to receivers
        """

        message_content = self.make_content(
            title, content, recipients, recipient_field, **(message_kwargs or {})
        )
        message = self.message_class(
            title=title, content=message_content, mark=mark, msg_type=self.id
        )
        self.perform_send(message, recipients, recipient_field, save=save, **kwargs)


def notify(
    recipients: typing.Optional[list[User]],
    title: str = None,
    message: str = None,
    template_code: str = None,
    context: dict = None,
    save: bool = False,
    backends: list[typing.Union[BaseNotificationBackend, str]] = None,
    recipient_field: typing.Union[str, typing.Callable] = None,
    message_kwargs: dict = None,
    **kwargs,
):
    if message is None and not message_kwargs and not all([template_code, context]):
        raise ValueError("You must provide message or template or message_kwargs.")

    if not backends:
        raise ValueError("You must provide at least one backend.")

    if not recipients and save:
        logger.warning("No recipients provided, `save=True` will be ignored.")

    for backend_cls in backends:
        if isinstance(backend_cls, str):
            backend_cls = import_string(backend_cls)

        if template_code:
            try:
                template = MessageTemplate.objects.get(code=template_code)
            except ObjectDoesNotExist:
                raise ValueError(f"Template: {template_code} doesn't exist.")
            # `kwargs` is prior to `kwargs` defined in template
            if template.backend_kwargs and isinstance(template.backend_kwargs, dict):
                backend_kwargs = template.backend_kwargs
                backend_kwargs.update(kwargs)
            else:
                backend_kwargs = kwargs

            backend = backend_cls(**backend_kwargs)
            backend.send_with_template(
                recipients,
                template,
                context,
                title=title,
                save=save,
                recipient_field=recipient_field,
                message_kwargs=message_kwargs,
            )
        else:
            backend = backend_cls(**kwargs)
            backend.send(
                title,
                recipients,
                message,
                save=save,
                recipient_field=recipient_field,
                message_kwargs=message_kwargs,
            )
