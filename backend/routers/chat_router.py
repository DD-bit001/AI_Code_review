from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas, auth, ai
from routers.review_router import get_default_provider

router = APIRouter(prefix="/api/projects/{project_id}/chat", tags=["chat"])

@router.post("/", response_model=schemas.ChatMessageResponse)
async def chat_with_project(project_id: int, request: schemas.ChatMessageRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    provider_config = get_default_provider(db, current_user.id)
    
    # Get all project files for context
    files = db.query(models.ProjectFile).filter(models.ProjectFile.project_id == project_id).all()
    
    session_id = request.session_id
    if not session_id:
        chat_session = models.ChatSession(project_id=project_id)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        session_id = chat_session.id
    
    # save user message
    user_msg = models.Message(session_id=session_id, role="user", content=request.content)
    db.add(user_msg)
    db.commit()
    
    history = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at).all()
    
    # perform AI request
    ai_response = await ai.chat_with_code(provider_config, files, history[:-1], request.content)
    
    # save ai message
    ai_msg = models.Message(session_id=session_id, role="assistant", content=ai_response)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return schemas.ChatMessageResponse(session_id=session_id, role="assistant", content=ai_response)

@router.get("/sessions", response_model=list[dict])
def get_chat_sessions(project_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    sessions = db.query(models.ChatSession).filter(models.ChatSession.project_id == project_id).all()
    return [{"id": s.id, "created_at": s.created_at} for s in sessions]

@router.get("/sessions/{session_id}/messages", response_model=list[schemas.ChatMessageResponse])
def get_chat_messages(project_id: int, session_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # simplified access check
    return db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at).all()
