from django.contrib import admin, messages
from django.contrib.admin import display
from django.db import models
from django.forms import Textarea
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Message, MessageTemplate, Notification

# Register your models here.


@admin.register(MessageTemplate)
class TemplateAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = ("name", "code", "title", "description")
    list_filter = ("code",)
    search_fields = ["code", "name"]
    fields = [
        "name",
        "code",
        "title",
        "description",
        "backend_kwargs",
        "message_kwargs",
        "content",
    ]
    ordering = ("-id",)

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 38})},
        models.JSONField: {"widget": Textarea(attrs={"rows": 2, "cols": 38})},
    }


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = [
        "to",
        "get_message_title",
        "has_read",
        "is_ignored",
        "is_sent",
        "updated_at",
    ]
    list_select_related = ["to", "message"]
    list_filter = ["to", "is_sent", "message__msg_type"]
    search_fields = ["message__mark"]
    autocomplete_fields = ["to", "message"]
    actions = ["send", "read", "ignore"]
    ordering = ("-id",)

    def has_change_permission(self, request, obj=None):
        return False

    def send(self, request, queryset):
        return NotImplemented

    def read(self, request, queryset):
        if queryset.count() > 0:
            queryset.update(has_read=True, updated_at=timezone.now())

        self.message_user(request, "Notification read", level=messages.SUCCESS)

    def ignore(self, request, queryset):
        if queryset.count() > 0:
            queryset.update(is_ignored=True, updated_at=timezone.now())

        self.message_user(request, "Notification ignored", level=messages.SUCCESS)

    @display(description=_("Template"))
    def get_message_template(self, obj):
        return obj.message.template

    @display(description=_("Render kwargs"))
    def get_message_render_kwargs(self, obj):
        return obj.message.render_kwargs

    @display(description=_("Title"))
    def get_message_title(self, obj):
        return obj.message.title

    @display(description=_("Message Mark"))
    def get_message_mark(self, obj):
        return obj.message.mark

    @display(description=_("Message type"))
    def get_message_type(self, obj):
        return obj.message.msg_type

    @display(description=_("Content"))
    def get_message_content(self, obj):
        return obj.message.content

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [(None, {"fields": ["to", "message"]})]

        return [
            (
                "Message",
                {
                    "fields": [
                        "get_message_title",
                        "get_message_type",
                        "get_message_mark",
                        "get_message_content",
                        "get_message_template",
                        "get_message_render_kwargs",
                    ]
                },
            ),
            (
                "Notification",
                {
                    "fields": [
                        "to",
                        "is_sent",
                        "has_read",
                        "is_ignored",
                        "notify_kwargs",
                        "created_at",
                        "updated_at",
                    ]
                },
            ),
        ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = [
        "title",
        "msg_type",
        "template",
        "mark",
        "created_at",
    ]
    list_filter = ("msg_type", "template")
    search_fields = ["mark", "title"]
    ordering = ("-id",)

    def has_change_permission(self, request, obj=None):
        return False
