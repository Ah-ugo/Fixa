from datetime import timedelta
from db import users_collection
from services.auth_service import hash_password, verify_password, create_access_token, authenticate_user
from bson import ObjectId
from services.email_service import EmailService

email_service = EmailService()

# Register user or provider
def register_user(data: dict):
    existing_user = users_collection.find_one({"email": data["email"]})
    if existing_user:
        return {"error": "Email already registered"}

    data["password"] = hash_password(data["password"])
    data["role"] = data.get("role", "user")
    data["created_at"] = data.get("created_at")
    result = users_collection.insert_one(data)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

# with email
# def register_user(data: dict):
#     existing_user = users_collection.find_one({"email": data["email"]})
#     if existing_user:
#         return {"error": "Email already registered"}
#
#     data["password"] = hash_password(data["password"])
#     data["role"] = data.get("role", "user")
#     data["created_at"] = datetime.now()
#     data["is_verified"] = False  # Email not verified yet
#
#     result = users_collection.insert_one(data)
#
#     # Send OTP for verification
#     email_service.send_otp_email(data["email"])
#
#     return {
#         "message": "User registered successfully. Please verify your email.",
#         "user_id": str(result.inserted_id)
#     }

# Login user
def login_user(email: str, password: str):
    user = authenticate_user(email, password)
    if not user:
        return {"error": "Invalid credentials"}

    token = create_access_token({"user_id": str(user["_id"]), "role": user["role"]},
                                expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}


# Logout user (invalidate token)
def logout_user():
    return {"message": "Logout successful"}  # Typically, frontend handles token invalidation


# Get current user profile
def get_current_user(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    user.pop("password")
    return user


# Update user profile
def update_profile(user_id: str, update_data: dict):
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    return {"message": "Profile updated successfully"}


# Switch role between user and provider
def switch_role(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    new_role = "provider" if user["role"] == "user" else "user"
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})
    return {"message": f"Role switched to {new_role}"}


def verify_otp(email: str, otp: str):
    return email_service.verify_otp(email, otp)


def forgot_password(email: str):

    user = users_collection.find_one({"email": email})
    if not user:
        return {"error": "Email not registered"}

    # Generate and send reset token
    token = email_service.generate_reset_token(email)
    email_service.send_password_reset_email(email, token)

    return {"message": "Password reset link sent to your email"}

# Reset password
def reset_password(email: str, new_password: str):
    hashed_password = hash_password(new_password)
    users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
    return {"message": "Password reset successful"}


# Delete account
def delete_account(user_id: str):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    return {"message": "Account deleted successfully"}
