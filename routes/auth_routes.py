from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from typing import Optional
from models.user import UserRegister, UserLogin, UpdateProfile, ResetPassword
from handlers.auth_handler import (
    register_user, login_user, logout_user,
    update_profile, switch_role, verify_otp, forgot_password, reset_password,
    delete_account
)
from services.monnify_service import create_reserved_account
from services.auth_service import get_current_user, authenticate_user, create_access_token
from services.cloudinary_service import upload_image
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 3600


# Register user or provider
@router.post("/register")
def register(
        full_name: str = Form(..., min_length=3, max_length=50),
        email: str = Form(...),
        password: str = Form(..., min_length=6, max_length=100),
        role: Optional[str] = Form("user"),
        phone_number: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        profile_image: Optional[UploadFile] = File(None)
):
    profile_image_url = None
    if profile_image:
        profile_image_url = upload_image(profile_image.file)

    user_data = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
        "phone_number": phone_number,
        "address": address,
        "profile_image": profile_image_url
    }

    result = register_user(user_data)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    # Create reserved account after successful registration
    reserved_account = create_reserved_account(
        account_reference=result["user_id"],
        account_name=full_name,
        customer_email=email,
        bvn="",  # If BVN is required, add it as a form field
        customer_name=full_name
    )
    return {"message": result["message"], "reserved_account": reserved_account}


# Login user
@router.post("/login")
def login(data: UserLogin):
    result = login_user(data.email, data.password)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result["error"])
    return result


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {"sub": str(user["_id"])},  # Correctly pass user ID in the data dict
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Logout user
@router.post("/logout")
def logout():
    return logout_user()


# Get current user profile
@router.get("/profile")
def profile(user: dict = Depends(get_current_user)):
    return user


# Update user profile
@router.put("/profile/update")
def update_profile_route(update_data: UpdateProfile, user: dict = Depends(get_current_user)):
    return update_profile(user["_id"], update_data.dict())


# Switch role between user and provider
@router.put("/switch-role")
def switch_role_route(user: dict = Depends(get_current_user)):
    return switch_role(user["_id"])


# Verify OTP for account activation
@router.post("/verify-otp")
def verify_otp_route(email: str, otp: str):
    return verify_otp(email, otp)


# Forgot password
@router.post("/forgot-password")
def forgot_password_route(email: str):
    return forgot_password(email)


# Reset password
@router.post("/reset-password")
def reset_password_route(data: ResetPassword):
    return reset_password(data.email, data.new_password)


# Delete account
@router.delete("/delete-account")
def delete_account_route(user: dict = Depends(get_current_user)):
    return delete_account(user["user_id"])
