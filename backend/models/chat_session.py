from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .chat_message import ChatMessage

class ChatSessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"

@dataclass
class ChatSession:
    """Represents a chat session between users."""
    session_id: str
    initiator_id: str
    recipient_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    status: ChatSessionStatus = ChatSessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    subject: Optional[str] = None

    def add_message(self, sender_id: str, content: str) -> ChatMessage:
        """Add a new message to the chat session."""
        message = ChatMessage(
            message_id=f"{self.session_id}_{len(self.messages)}",
            sender_id=sender_id,
            content=content
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
        return message

    def mark_messages_as_read(self, user_id: str) -> int:
        """Mark all unread messages for a user as read."""
        count = 0
        for message in self.messages:
            if not message.is_read and message.sender_id != user_id:
                message.is_read = True
                count += 1
        return count

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread messages for a user."""
        return sum(1 for msg in self.messages 
                  if not msg.is_read and msg.sender_id != user_id)

    def update_status(self, new_status: ChatSessionStatus) -> None:
        """Update the chat session status."""
        self.status = new_status
        self.last_activity = datetime.now()

    def archive(self) -> None:
        """Archive the chat session."""
        self.status = ChatSessionStatus.ARCHIVED
        self.last_activity = datetime.now()

    def is_participant(self, user_id: str) -> bool:
        """Check if a user is a participant in this chat session."""
        return user_id in (self.initiator_id, self.recipient_id)

    def get_other_participant(self, user_id: str) -> Optional[str]:
        """Get the ID of the other participant in the chat."""
        if user_id == self.initiator_id:
            return self.recipient_id
        elif user_id == self.recipient_id:
            return self.initiator_id
        return None 