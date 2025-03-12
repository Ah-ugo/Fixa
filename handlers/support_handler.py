from db import support_tickets_collection
from datetime import datetime
from bson import ObjectId

# Submit a support ticket
def submit_support_ticket(user_id: str, subject: str, message: str):
    ticket = {
        "user_id": user_id,
        "subject": subject,
        "message": message,
        "status": "open",
        "created_at": datetime.utcnow()
    }
    result = support_tickets_collection.insert_one(ticket)
    return {"ticket_id": str(result.inserted_id), "message": "Support ticket submitted successfully."}

# View ticket details
def get_support_ticket(ticket_id: str):
    ticket = support_tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return {"error": "Ticket not found"}
    ticket["_id"] = str(ticket["_id"])
    return ticket

# Update ticket status
def update_support_ticket(ticket_id: str, status: str):
    result = support_tickets_collection.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        return {"error": "Ticket not found"}
    return {"message": "Ticket status updated successfully."}

# Delete a support ticket
def delete_support_ticket(ticket_id: str):
    result = support_tickets_collection.delete_one({"_id": ObjectId(ticket_id)})
    if result.deleted_count == 0:
        return {"error": "Ticket not found"}
    return {"message": "Support ticket deleted successfully."}