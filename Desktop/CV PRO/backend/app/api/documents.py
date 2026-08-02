"""Document management - Resume/CV uploads (Simplified)"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import os
from datetime import datetime
import shutil

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = "/tmp/careerosai/uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
print(f"✅ Documents API ready: {UPLOAD_DIR}")

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(default="unknown")
):
    """Upload resume/CV file - Simple file storage without database"""

    try:
        print(f"📤 Uploading file: {file.filename} for user: {user_id}")

        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        filename_lower = file.filename.lower()
        allowed_extensions = ('.pdf', '.doc', '.docx', '.txt', '.py', '.js', '.json', '.md')

        if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
            )

        # Read file content
        contents = await file.read()

        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024:.1f}MB, got {len(contents) / 1024 / 1024:.1f}MB)"
            )

        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        # Save file
        safe_filename = file.filename.replace(" ", "_")
        file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{safe_filename}")

        print(f"💾 Saving to: {file_path}")

        with open(file_path, "wb") as f:
            f.write(contents)

        # Verify file was saved
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to save file")

        file_size = os.path.getsize(file_path)

        print(f"✅ File saved successfully: {file_path} ({file_size} bytes)")

        return {
            "status": "success",
            "filename": file.filename,
            "file_size": file_size,
            "upload_time": datetime.utcnow().isoformat(),
            "message": "✅ Resume uploaded successfully!"
        }

    except HTTPException as e:
        print(f"❌ HTTP Error: {e.detail}")
        raise e
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/resume/{user_id}")
async def get_resume(user_id: str):
    """Get user's resume info"""

    try:
        # Find resume files for user
        if not os.path.exists(UPLOAD_DIR):
            raise HTTPException(status_code=404, detail="No uploads directory")

        files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(f"{user_id}_")]

        if not files:
            raise HTTPException(status_code=404, detail="Resume not found")

        latest_file = files[-1]  # Get latest
        file_path = os.path.join(UPLOAD_DIR, latest_file)
        file_size = os.path.getsize(file_path)

        return {
            "filename": latest_file,
            "file_size": file_size,
            "uploaded_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "message": "✅ Resume found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/resume/{user_id}")
async def delete_resume(user_id: str):
    """Delete user's resume"""

    try:
        if not os.path.exists(UPLOAD_DIR):
            raise HTTPException(status_code=404, detail="No uploads directory")

        files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(f"{user_id}_")]

        if not files:
            raise HTTPException(status_code=404, detail="Resume not found")

        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file)
            if os.path.exists(file_path):
                os.remove(file_path)

        return {"status": "deleted", "message": "✅ Resume deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
