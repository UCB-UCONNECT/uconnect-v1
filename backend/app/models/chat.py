"""
Models relacionados a chat e mensagens.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base
from .base import ConversationType, conversation_participants


class Conversation(Base):
    __tablename__ = "Conversation"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    type = Column(Enum(ConversationType), nullable=False, default=ConversationType.direct)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    participants = relationship("User", secondary=conversation_participants, back_populates="conversations")
    channel = relationship("Channel", uselist=False, back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_conversation_type", "type"),
        Index("idx_conversation_updated", "updatedAt"),
    )


class Channel(Base):
    __tablename__ = 'Channel'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    conversationId = Column(Integer, ForeignKey("Conversation.id", ondelete="CASCADE"))
    
    conversation = relationship("Conversation", back_populates="channel")
    subchannels = relationship("Subchannel", back_populates="parent_channel", cascade="all, delete-orphan")


class Subchannel(Base):
    __tablename__ = 'Subchannel'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parentChannelId = Column(Integer, ForeignKey("Channel.id", ondelete="CASCADE"))
    
    parent_channel = relationship("Channel", back_populates="subchannels")
    messages = relationship("Message", back_populates="subchannel", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "Message"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    subchannelId = Column(Integer, ForeignKey("Subchannel.id", ondelete="CASCADE"), nullable=False)
    authorId = Column(Integer, ForeignKey("User.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    isRead = Column(Boolean, default=False, nullable=False)
    
    subchannel = relationship("Subchannel", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")
    
    __table_args__ = (
        Index("idx_message_subchannel", "subchannelId"),
        Index("idx_message_timestamp", "timestamp"),
        Index("idx_message_author", "authorId"),
    )
