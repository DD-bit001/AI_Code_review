from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas, auth

router = APIRouter(prefix="/api/providers", tags=["providers"])

@router.post("/", response_model=schemas.AIProviderResponse)
def create_provider(provider: schemas.AIProviderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if provider.is_default:
        # unset others
        db.query(models.AIProvider).filter(models.AIProvider.owner_id == current_user.id).update({"is_default": False})
        
    new_provider = models.AIProvider(**provider.dict(), owner_id=current_user.id)
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return new_provider

@router.get("/", response_model=list[schemas.AIProviderResponse])
def get_providers(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.AIProvider).filter(models.AIProvider.owner_id == current_user.id).all()

@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    provider = db.query(models.AIProvider).filter(models.AIProvider.id == provider_id, models.AIProvider.owner_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    db.delete(provider)
    db.commit()
    return {"message": "Provider deleted successfully"}
