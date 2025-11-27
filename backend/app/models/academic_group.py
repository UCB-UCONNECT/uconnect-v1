"""
Model de grupos acadêmicos.
"""
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from ..db.base import Base
from .base import academic_group_user_association


class AcademicGroup(Base):
    __tablename__ = "AcademicGroup"
    
    id = Column(Integer, primary_key=True, index=True)
    course = Column(String(100), nullable=False)
    classGroup = Column(String(50), nullable=False, unique=True, index=True)
    subject = Column(String(100), nullable=False)
    
    users = relationship("User", secondary=academic_group_user_association, back_populates="groups")
