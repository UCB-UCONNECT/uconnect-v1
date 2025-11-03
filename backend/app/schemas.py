# ---------------- SCHEMAS (MODELOS DE DADOS) Pydantic ---------------- #
"""
Este arquivo, schemas.py, define os modelos de dados (schemas) da API
utilizando a biblioteca Pydantic.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date, time
from typing import Optional, List
from .models import UserRole, AccessStatus

# --- Schemas de Autenticação ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    registration: Optional[str] = None

class UserLogin(BaseModel):
    registration: str
    password: str

# --- Schemas de Usuário ---
class UserBase(BaseModel):
    registration: str
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    accessStatus: AccessStatus
    createdAt: datetime
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    accessStatus: Optional[AccessStatus] = None

class UserStatusUpdate(BaseModel):
    accessStatus: AccessStatus

class UserRoleUpdate(BaseModel):
    role: str

# --- Schemas de Eventos (Calendário) ---
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    eventDate: date
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    academicGroupId: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    date: date
    hora: Optional[str] = None
    description: Optional[str] = None
    local: Optional[str] = None
    academicGroupId: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    eventDate: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    academicGroupId: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    timestamp: datetime
    eventDate: date
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    academicGroupId: Optional[str] = None
    creatorId: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Grupos Acadêmicos ---
class AcademicGroupBase(BaseModel):
    course: str
    classGroup: str
    subject: str

class AcademicGroupCreate(AcademicGroupBase):
    pass

class AcademicGroupUpdate(AcademicGroupBase):
    pass

class AcademicGroupResponse(AcademicGroupBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AcademicGroupDetailResponse(AcademicGroupResponse):
    users: List[UserResponse] = []

# --- Schemas de Publicações (Posts) ---
class PostBase(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=3)

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3)
    content: Optional[str] = Field(None, min_length=3)

class PostResponse(PostBase):
    id: int
    date: datetime
    author: UserResponse
    model_config = ConfigDict(from_attributes=True)

# --- Esquemas para Mensagens ---
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    authorId: int
    authorName: Optional[str] = None  # <- Nome do autor
    model_config = ConfigDict(from_attributes=True)

# --- Esquemas para Conversas (Chat) ---
class UserSimple(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class Chat(BaseModel):
    id: int
    title: str
    participants: List[UserSimple]
    last_message: Optional[Message] = None
    model_config = ConfigDict(from_attributes=True)

class ChatCreate(BaseModel):
    participant_ids: List[int]
    title: Optional[str] = None