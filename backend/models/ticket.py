from dataclasses import dataclass
from datetime import datetime

@dataclass
class Ticket:
    """Class representing order and billing receipts."""
    ticket_id: str
    order_id: str
    bill_id: str
    printed_at: datetime
    content: str 