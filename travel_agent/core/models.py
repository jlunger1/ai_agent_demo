from django.db import models
import uuid

class ToolMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "search_flights"
    description = models.TextField()  # e.g., "Search for flights between two cities on a specific date."
    parameters = models.JSONField()  # e.g., {"origin": "The IATA airport code...", "destination": "..."}
    tool_class = models.CharField(max_length=50)  # e.g., "AmadeusTool"

    def __str__(self):
        return f"{self.tool_class}.{self.name}"


class Conversation(models.Model):
    """
    Represents a conversation between a user and the TravelAgent.
    """
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.session_id}"


class ConversationMessage(models.Model):
    """
    Represents a single message in a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.CharField(
        max_length=10,
        choices=[("user", "User"), ("assistant", "Assistant")],
    )  # Indicates the sender of the message
    content = models.TextField()  # The message text
    tool = models.ForeignKey(
        ToolMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )  # Optional: Tool used in the message
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.conversation} at {self.created_at}"
