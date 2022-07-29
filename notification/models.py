from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_quill.fields import QuillField


class NotificationQuerySet(models.QuerySet):
    def read(self):
        """
        return read notification messages
        """
        return self.filter(has_read=True)

    def unread(self, user):
        """
        return unread notification messages
        """
        return self.filter(has_read=False)

    def ignored(self):
        """
        Return ignored notification messages
        """
        return self.filter(is_ignored=True)

    def sent(self):
        """
        Return sent notification messages
        """
        return self.filter(is_sent=True)

    def unsent(self):
        """
        Return unsent notification messages
        """
        return self.filter(is_sent=False)


class Notification(models.Model):
    has_read = models.BooleanField(verbose_name=_("Read Or Not"), default=False)
    is_ignored = models.BooleanField(verbose_name=_("Ignored Or Not"), default=False)
    is_sent = models.BooleanField(verbose_name=_("Sent Or Not"), default=False)
    to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Receiver"),
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    message = models.ForeignKey(
        "Message",
        verbose_name=_("Message"),
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name="notifications",
    )
    notify_kwargs = models.JSONField(
        verbose_name=_("Notify Kwargs"), blank=True, default=dict
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = _("Notification")
        db_table = "notification"

    def __str__(self):
        return str(self.message)

    def mark_as_read(self):
        """
        Mark a notification message as read.
        """
        self.has_read = True
        self.save(update_fields=["has_read", "updated_at"])

    def mark_as_unread(self):
        """
        Mark a notification message as unread.
        """
        self.has_read = False
        self.save(update_fields=["has_read", "updated_at"])

    def mark_as_sent(self):
        """
        Mark a notification message as sent.
        """
        self.is_sent = True
        self.save(update_fields=["is_sent", "updated_at"])

    def mark_as_ignored(self):
        """
        Mark a notification message as ignored.
        """
        self.is_ignored = True
        self.save(update_fields=["is_ignored", "updated_at"])


class MessageTemplate(models.Model):
    """
    Message template
    """

    name = models.CharField(max_length=64, verbose_name=_("Template Name"))
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    code = models.CharField(max_length=4, verbose_name=_("Template Code"), unique=True)
    title = models.CharField(
        max_length=64, verbose_name=_("Message Title"), null=True, blank=True
    )
    content = QuillField(verbose_name=_("Template Content"))
    backend_kwargs = models.JSONField(
        verbose_name=_("Backend Kwargs"), blank=True, default=dict
    )
    message_kwargs = models.JSONField(
        verbose_name=_("Message Kwargs"), blank=True, default=dict
    )

    objects = models.Manager()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _("Message Template")
        db_table = "message_template"

    def mark_as_read(self):
        self.has_read = True
        self.save(update_fields=["has_read", "updated_at"])

    def mark_as_unread(self):
        self.has_read = False
        self.save(update_fields=["has_read", "updated_at"])

    def mark_as_sent(self):
        self.is_sent = True
        self.save(update_fields=["is_sent", "updated_at"])

    def mark_as_unsent(self):
        self.is_sent = False
        self.save(update_fields=["is_sent", "updated_at"])

    def mark_as_ignored(self):
        self.is_ignored = True
        self.save(update_fields=["is_ignored", "updated_at"])


class Message(models.Model):
    """
    Message
    """

    title = models.CharField(
        max_length=64, null=True, blank=True, verbose_name=_("Title")
    )
    mark = models.CharField(
        max_length=64,
        verbose_name=_("Message Mark"),
        null=True,
        blank=True,
        db_index=True,
    )
    msg_type = models.CharField(
        max_length=64, verbose_name=_("Message Type"), db_index=True
    )
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    template = models.ForeignKey(
        MessageTemplate,
        verbose_name=_("Template"),
        db_constraint=False,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    render_kwargs = models.JSONField(
        verbose_name=_("Render Kwargs"),
        blank=True,
        default=dict,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    objects = models.Manager()

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = _("Message")
        db_table = "message"
