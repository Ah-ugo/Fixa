from fastapi import APIRouter, HTTPException, Depends
from handlers.support_handler import (
    submit_support_ticket,
    get_support_ticket,
    update_support_ticket,
    delete_support_ticket,
)
from models.user import User  # Assuming user model contains role-based access
from services.auth_service import get_current_user  # Function to get authenticated user

router = APIRouter()


# Submit a support ticket (Users only)
@router.post("/")
def submit_ticket(user: User = Depends(get_current_user), subject: str = "", message: str = ""):
    return submit_support_ticket(user.id, subject, message)


# View ticket details (Any authenticated user)
@router.get("/{ticket_id}")
def get_ticket(ticket_id: str, user: User = Depends(get_current_user)):
    ticket = get_support_ticket(ticket_id)
    if "error" in ticket:
        raise HTTPException(status_code=404, detail=ticket["error"])
    return ticket


# Update ticket status (Admins only)
@router.patch("/{ticket_id}")
def update_ticket(ticket_id: str, status: str, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    response = update_support_ticket(ticket_id, status)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response


# Delete a support ticket (Users can delete their own, Admins can delete any)
@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: str, user: User = Depends(get_current_user)):
    ticket = get_support_ticket(ticket_id)

    if "error" in ticket:
        raise HTTPException(status_code=404, detail=ticket["error"])

    if user.role != "admin" and ticket["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Access denied. You can only delete your own ticket.")

    response = delete_support_ticket(ticket_id)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response
