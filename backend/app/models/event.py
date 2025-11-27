"""
Model de eventos.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..db.base import Base


class Event(Base):
    __tablename__ = "Event"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    eventDate = Column(Date, nullable=False)
    startTime = Column(Time, nullable=True)
    endTime = Column(Time, nullable=True)
    academicGroupId = Column(String(50), nullable=True)
    creatorId = Column(Integer, ForeignKey("User.id", ondelete="SET NULL"), nullable=True)
    
    creator = relationship("User", back_populates="events_created")
    
    def __init__(self, **kwargs):
        from datetime import datetime
        
        # Compatibilidade snake_case para fixtures/testes
        if 'event_date' in kwargs:
            kwargs['eventDate'] = kwargs.pop('event_date')
        if 'scheduled_date' in kwargs:
            kwargs['eventDate'] = kwargs.pop('scheduled_date')
        if 'start_time' in kwargs:
            kwargs['startTime'] = kwargs.pop('start_time')
        if 'end_time' in kwargs:
            kwargs['endTime'] = kwargs.pop('end_time')
        if 'academic_group_id' in kwargs:
            kwargs['academicGroupId'] = kwargs.pop('academic_group_id')
        if 'creator_id' in kwargs:
            kwargs['creatorId'] = kwargs.pop('creator_id')
        
        # Preencher timestamp automaticamente se não fornecido
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = datetime.now()
        
        # Filtrar apenas campos que existem no model
        valid_attrs = {k: v for k, v in kwargs.items() if hasattr(type(self), k)}
        super().__init__(**valid_attrs)
    
    __table_args__ = (
        Index("idx_event_date", "eventDate"),
        Index("idx_event_timestamp", "timestamp"),
        Index("idx_event_creator", "creatorId"),
    )
