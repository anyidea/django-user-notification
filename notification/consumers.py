from channels.generic.websocket import AsyncJsonWebsocketConsumer

from notification.utils import get_group_name


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    This notify consumer handles websocket connections for single user client.
    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    async def connect(self):
        await self.channel_layer.group_add(
            get_group_name(self.scope["user"].pk), self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            get_group_name(self.scope["user"].pk), self.channel_name
        )

    async def notify_message(self, event):
        """
        Send message to WebSocket
        """
        await self.send_json(
            {
                "msgtype": event["msgtype"],
                "title": event["title"],
                "message": event["message"],
            }
        )
