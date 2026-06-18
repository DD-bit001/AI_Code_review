from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas, auth, ai
import json

router = APIRouter(prefix="/api/projects/{project_id}/reviews", tags=["reviews"])

def get_default_provider(db: Session, owner_id: int):
    provider = db.query(models.AIProvider).filter(models.AIProvider.owner_id == owner_id, models.AIProvider.is_default == True).first()
    if not provider:
        provider = db.query(models.AIProvider).filter(models.AIProvider.owner_id == owner_id).first()
    if not provider:
        raise HTTPException(status_code=400, detail="No AI provider configured. Please configure one in settings.")
    return {
        "base_url": provider.base_url,
        "api_key": provider.api_key,
        "model_name": provider.model_name
    }

@router.post("/", response_model=schemas.ReviewResponse)
async def create_review(project_id: int, request: schemas.ReviewRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    provider_config = get_default_provider(db, current_user.id)
    
    query = db.query(models.ProjectFile).filter(models.ProjectFile.project_id == project_id)
    if "ALL" not in request.target_files:
        query = query.filter(models.ProjectFile.file_path.in_(request.target_files))
        
    files = query.all()
    if not files:
        raise HTTPException(status_code=400, detail="No files selected or found for review")
        
    if request.review_mode == "Architecture Analysis":
        analysis = await ai.generate_architecture_analysis(provider_config, files)
        review_data = {
            "summary": "Architecture Analysis Generated",
            "issues": [],
            "recommendations": [analysis]
        }
    elif request.review_mode == "Documentation Generator":
        docs = await ai.generate_documentation(provider_config, files)
        review_data = {
            "summary": "Documentation Generated",
            "issues": [],
            "recommendations": [docs]
        }
    else:
        review_data = await ai.perform_code_review(provider_config, files, request.review_mode)
        
    new_review = models.Review(
        project_id=project_id,
        review_type=request.review_mode,
        target_files=json.dumps(request.target_files),
        summary=review_data.get("summary", ""),
        issues=json.dumps(review_data.get("issues", [])),
        recommendations=json.dumps(review_data.get("recommendations", []))
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return new_review

@router.get("/", response_model=list[schemas.ReviewResponse])
def get_reviews(project_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return db.query(models.Review).filter(models.Review.project_id == project_id).order_by(models.Review.created_at.desc()).all()

@router.get("/{review_id}", response_model=schemas.ReviewResponse)
def get_review(project_id: int, review_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    review = db.query(models.Review).join(models.Project).filter(models.Review.id == review_id, models.Project.owner_id == current_user.id, models.Project.id == project_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
