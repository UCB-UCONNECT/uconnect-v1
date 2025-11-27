"""
Models de publicações (posts e comunicados).
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base


class Post(Base):
    __tablename__ = "Post"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    authorId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    
    author = relationship("User", back_populates="posts")
    
    __table_args__ = (
        Index("idx_post_date", "date"),
    )


class Announcement(Base):
    __tablename__ = "Announcement"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    authorId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    
    author = relationship("User", back_populates="announcements")
    
    __table_args__ = (
        Index("idx_announcement_date", "date"),
    )
