from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routes.wallet_routes import router as wallet_router
from routes.service_routes import router as service_router
from routes.support_routes import router as support_ticket_router
# from routes.users import router as user_router
from routes.booking_routes import router as booking_router
from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.notification_routes import router as notifications_router
from routes.provider_routes import router as provider_router
from routes.review_routes import router as review_router

app = FastAPI(
    title="Fixa API",
    version="1.0.0",
    description="API for managing services, bookings, payments, support tickets, and user wallets."
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(wallet_router, prefix="/api/wallets", tags=["Wallets"])
app.include_router(service_router, prefix="/api/services", tags=["Services"])
app.include_router(support_ticket_router, prefix="/api/support-tickets", tags=["Support Tickets"])
app.include_router(admin_router, prefix="/api/admin", tags=["Users"])
app.include_router(booking_router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(provider_router, prefix="/api/providers", tags=["Providers"])
app.include_router(review_router, prefix="/api/review", tags=["Reviews"])

@app.get("/")
def root():
    return {"message": "Welcome to the All-Purpose Services API"}


