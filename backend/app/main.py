from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.controllers import (
    auth_controller,
    user_controller,
    product_controller,
    order_controller,
    payment_controller,
    category_controller,
    notification_controller
)
from app.config import DATABASE_URL
from app.database import engine, Base

app = FastAPI(
    title="OrderMe API",
    description="API for OrderMe service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_controller.router, prefix="/users", tags=["Users"])
app.include_router(product_controller.router, prefix="/products", tags=["Products"])
app.include_router(order_controller.router, prefix="/orders", tags=["Orders"])
app.include_router(payment_controller.router, prefix="/payments", tags=["Payments"])
app.include_router(category_controller.router, prefix="/categories", tags=["Categories"])
app.include_router(notification_controller.router, prefix="/notifications", tags=["Notifications"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )

@app.on_event("startup")
async def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Add any other startup tasks here

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    # Add any cleanup tasks here
    pass
