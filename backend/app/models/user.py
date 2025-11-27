"""
Models relacionados a usuários, autenticação e acesso.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base
from .base import UserRole, AccessStatus, academic_group_user_association, conversation_participants


class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    passwordHash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    accessStatus = Column(Enum(AccessStatus), default=AccessStatus.active, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, **kwargs):
        # Compatibilidade snake_case para fixtures/testes antigos
        if 'hashed_password' in kwargs:
            kwargs['passwordHash'] = kwargs.pop('hashed_password')
        if 'created_at' in kwargs:
            kwargs['createdAt'] = kwargs.pop('created_at')
        if 'updated_at' in kwargs:
            kwargs['updatedAt'] = kwargs.pop('updated_at')
        if 'access_status' in kwargs:
            kwargs['accessStatus'] = kwargs.pop('access_status')
        super().__init__(**kwargs)
    
    # Relationships
    events_created = relationship("Event", back_populates="creator")
    groups = relationship("AcademicGroup", secondary=academic_group_user_association, back_populates="users")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="author", cascade="all, delete-orphan")
    conversations = relationship("Conversation", secondary=conversation_participants, back_populates="participants")
    messages_sent = relationship("Message", back_populates="sender")
    
    __table_args__ = (
        Index("ix_users_registration", "registration"),
        Index("ix_users_email", "email"),
    )


class AccessManager(Base):
    __tablename__ = "AccessManager"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("User.id"), nullable=False)
    permission = Column(String(255), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "Session"
    
    token = Column(String(500), primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("User.id"), nullable=False, index=True)
    startDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    expirationDate = Column(DateTime, nullable=False)
    
    user = relationship("User", lazy="joined")
