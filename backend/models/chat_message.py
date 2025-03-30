from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChatMessage:
    """Class representing individual chat messages."""
    message_id: str
    chat_session_id: str
    sender_id: str
    content: str
    timestamp: datetime 