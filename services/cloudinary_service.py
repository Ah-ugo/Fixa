import cloudinary
import cloudinary.uploader
import os

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Upload Image
def upload_image(image_path, folder="service_app"):
    try:
        response = cloudinary.uploader.upload(image_path, folder=folder)
        return response.get("secure_url")
    except Exception as e:
        return {"error": str(e)}

# Delete Image
def delete_image(public_id):
    try:
        response = cloudinary.uploader.destroy(public_id)
        return response
    except Exception as e:
        return {"error": str(e)}

# Upload Base64 Image
def upload_base64_image(base64_string, folder="service_app"):
    try:
        response = cloudinary.uploader.upload(base64_string, folder=folder)
        return response.get("secure_url")
    except Exception as e:
        return {"error": str(e)}
