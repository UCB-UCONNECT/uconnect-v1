"""
Enums e tabelas de associação compartilhadas entre models.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
import enum
from datetime import datetime
from ..db.base import Base


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    coordinator = "coordinator"
    admin = "admin"


class AccessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class ConversationType(str, enum.Enum):
    direct = "direct"
    group = "group"
    support = "support"


# Tabelas de associação many-to-many
academic_group_user_association = Table(
    'AcademicGroup_User',
    Base.metadata,
    Column('groupId', Integer, ForeignKey('AcademicGroup.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True)
)

conversation_participants = Table(
    'Conversation_Participants',
    Base.metadata,
    Column('conversationId', Integer, ForeignKey('Conversation.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True),
    Column('joinedAt', DateTime, default=datetime.utcnow, nullable=False)
)


# Aliases MAIÚSCULOS para compatibilidade com código legado/testes
UserRole.STUDENT = UserRole.student
UserRole.TEACHER = UserRole.teacher
UserRole.COORDINATOR = UserRole.coordinator
UserRole.ADMIN = UserRole.admin

AccessStatus.ACTIVE = AccessStatus.active
AccessStatus.INACTIVE = AccessStatus.inactive
AccessStatus.SUSPENDED = AccessStatus.suspended

ConversationType.DIRECT = ConversationType.direct
ConversationType.GROUP = ConversationType.group
ConversationType.SUPPORT = ConversationType.support
