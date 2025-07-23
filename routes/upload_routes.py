from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import os
from models.upload import ImageUploadResponse
from services.auth_service import get_current_user
from services.cloudinary_service import upload_image, delete_image, upload_base64_image
import tempfile

router = APIRouter()


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image_file(
        file: UploadFile = File(...),
        folder: Optional[str] = "service_app",
        current_user: dict = Depends(get_current_user)
):
    """
    Upload an image file to Cloudinary

    Args:
        file: The image file to upload
        folder: Cloudinary folder to store the image (default: 'service_app')

    Returns:
        URL of the uploaded image
    """
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        # Upload to Cloudinary
        image_url = upload_image(temp_path, folder=folder)

        # Clean up temporary file
        os.unlink(temp_path)

        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])

        return {"url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/base64", response_model=ImageUploadResponse)
async def upload_base64_image(
        base64_string: str,
        folder: Optional[str] = "service_app",
        current_user: dict = Depends(get_current_user)
):
    """
    Upload an image from base64 string to Cloudinary

    Args:
        base64_string: The image encoded as base64 string
        folder: Cloudinary folder to store the image (default: 'service_app')

    Returns:
        URL of the uploaded image
    """
    try:
        image_url = upload_base64_image(base64_string, folder=folder)

        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])

        return {"url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/image")
async def delete_cloudinary_image(
        public_id: str,
        current_user: dict = Depends(get_current_user)
):
    """
    Delete an image from Cloudinary

    Args:
        public_id: The public ID of the image to delete

    Returns:
        Result of the deletion operation
    """
    try:
        result = delete_image(public_id)

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"success": True, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))