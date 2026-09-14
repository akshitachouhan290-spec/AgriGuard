from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    return JSONResponse(
        {
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "Image uploaded successfully"
        }
    )