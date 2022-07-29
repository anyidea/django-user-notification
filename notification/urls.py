from django.urls import re_path

from notification.consumers import NotificationConsumer

wspatterns = [
    re_path(r"^notify/message/$", NotificationConsumer.as_asgi()),
]
