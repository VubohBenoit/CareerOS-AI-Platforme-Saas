"""Document management - Resume/CV uploads"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.document import Document
from app.models.user import User
import os
from datetime import datetime
import shutil

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = "/tmp/careerosai/uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Upload resume/CV file"""
    
    try:
        # Validate file
        if not file.filename.endswith(('.pdf', '.doc', '.docx', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOC, DOCX, TXT files allowed"
            )
        
        # Check file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024}MB)"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Save to database
        doc = Document(
            id=f"doc_{datetime.now().timestamp()}",
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(contents),
            file_type=file.content_type,
            uploaded_at=datetime.utcnow(),
            document_metadata={"original_name": file.filename}
        )
        db.add(doc)
        db.commit()
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_size": len(contents),
            "upload_time": datetime.utcnow().isoformat(),
            "message": "✅ Resume uploaded successfully!"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/resume/{user_id}")
async def get_resume(user_id: str, db: Session = Depends(get_db)):
    """Get user's resume"""
    
    doc = db.query(Document).filter(Document.user_id == user_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "filename": doc.filename,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "file_size": doc.file_size,
        "file_type": doc.file_type
    }

@router.delete("/resume/{user_id}")
async def delete_resume(user_id: str, db: Session = Depends(get_db)):
    """Delete user's resume"""
    
    doc = db.query(Document).filter(Document.user_id == user_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    
    # Delete from database
    db.delete(doc)
    db.commit()
    
    return {"status": "deleted", "message": "✅ Resume deleted"}

@router.post("/extract-skills")
async def extract_skills(
    file: UploadFile = File(...),
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Upload resume and extract skills"""
    
    try:
        contents = await file.read()
        
        # Simple text extraction (in production, use proper PDF parsing)
        text = contents.decode('utf-8', errors='ignore')
        
        # Mock skill extraction
        skills = []
        common_skills = [
            "Python", "JavaScript", "React", "Node.js", "SQL",
            "AWS", "Docker", "Git", "API", "REST", "GraphQL",
            "Machine Learning", "Data Science", "FastAPI", "Django",
            "TypeScript", "Next.js", "PostgreSQL", "MongoDB"
        ]
        
        for skill in common_skills:
            if skill.lower() in text.lower():
                skills.append(skill)
        
        return {
            "filename": file.filename,
            "extracted_skills": skills if skills else ["Resume processed - add skills manually"],
            "confidence": 0.85 if skills else 0.5,
            "message": "✅ Skills extracted from resume"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Skill extraction failed: {str(e)}"
        )
