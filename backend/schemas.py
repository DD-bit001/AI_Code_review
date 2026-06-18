from pydantic import BaseModel
from typing import List, Optional, Any
import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    creation_date: datetime.datetime
    owner_id: int
    class Config:
        from_attributes = True

class ProjectFileResponse(BaseModel):
    id: int
    file_path: str
    content: str
    class Config:
        from_attributes = True

class AIProviderBase(BaseModel):
    name: str
    base_url: str
    api_key: Optional[str] = None
    model_name: str
    is_default: bool = False

class AIProviderCreate(AIProviderBase):
    pass

class AIProviderResponse(AIProviderBase):
    id: int
    class Config:
        from_attributes = True

class ReviewRequest(BaseModel):
    target_files: List[str] # List of file paths, or ["ALL"] for entire project
    review_mode: str # e.g. "Security", "Performance", "Code Quality", "Documentation Generator", "Architecture Analysis"

class Issue(BaseModel):
    severity: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

class ReviewResponse(BaseModel):
    id: int
    project_id: int
    review_type: str
    target_files: str
    summary: str
    issues: str # JSON encoded list of issues
    recommendations: str # JSON encoded list of recommendations
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ChatMessageRequest(BaseModel):
    session_id: Optional[int] = None
    content: str

class ChatMessageResponse(BaseModel):
    session_id: int
    role: str
    content: str
    class Config:
        from_attributes = True
