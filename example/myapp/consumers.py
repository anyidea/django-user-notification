from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    This notify consumer handles websocket connections for single user client.
    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Is the user logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
            # Get the group to which user is to be subscribed.
            self.group_name = self.scope["user"].group_name
            # Join the group
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify_message(self, event):
        """
        Send message to WebSocket
        """
        await self.send_json(
            {
                "msg_type": "notification",
                "message": event["message"],
            }
        )

    async def receive_json(self, content, **kwargs):
        """
        Receive decoded JSON content from WebSocket
        """
        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "notify.message",
                "message": content["message"],
            },
        )
