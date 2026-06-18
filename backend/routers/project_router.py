from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import database, models, schemas, auth
import zipfile
import io
import os

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_project = models.Project(**project.dict(), owner_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/upload")
def upload_files(project_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported for upload")
    
    content = file.file.read()
    
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                
                # Filter out obvious binary files or large files to prevent DB bloat
                ext = os.path.splitext(file_info.filename)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.exe', '.dll', '.zip', '.tar', '.gz']:
                    continue
                
                try:
                    file_content = zip_ref.read(file_info.filename).decode('utf-8')
                except UnicodeDecodeError:
                    continue # Skip binary or non-utf8 files
                
                project_file = models.ProjectFile(
                    project_id=project_id,
                    file_path=file_info.filename,
                    content=file_content
                )
                db.add(project_file)
            db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process zip file: {str(e)}")
        
    return {"message": "Files uploaded successfully"}

@router.get("/{project_id}/files", response_model=list[schemas.ProjectFileResponse])
def get_project_files(project_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = db.query(models.ProjectFile).filter(models.ProjectFile.project_id == project_id).all()
    return files
