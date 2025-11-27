"""
Models do uconnect-v1 (modularizados por domínio).

Estrutura:
- base.py: Enums e tabelas de associação
- user.py: User, AccessManager, Session
- event.py: Event
- academic_group.py: AcademicGroup
- publication.py: Post, Announcement
- chat.py: Conversation, Channel, Subchannel, Message
"""
# Enums e tabelas de associação
from .base import (
    UserRole,
    AccessStatus,
    ConversationType,
    academic_group_user_association,
    conversation_participants
)

# Models por domínio
from .user import User, AccessManager, Session
from .event import Event
from .academic_group import AcademicGroup
from .publication import Post, Announcement
from .chat import Conversation, Channel, Subchannel, Message

__all__ = [
    # Enums
    "UserRole",
    "AccessStatus",
    "ConversationType",
    # Tabelas de associação
    "academic_group_user_association",
    "conversation_participants",
    # User domain
    "User",
    "AccessManager",
    "Session",
    # Event domain
    "Event",
    # Academic group domain
    "AcademicGroup",
    # Publication domain
    "Post",
    "Announcement",
    # Chat domain
    "Conversation",
    "Channel",
    "Subchannel",
    "Message",
]
