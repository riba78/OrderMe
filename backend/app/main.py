from dotenv import load_dotenv
load_dotenv()  # This loads .env from the backend root by default

from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Users & Auth API",
    description="API for user management, authentication, and profile services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and user management routes
app.include_router(auth_router)
app.include_router(user_router)

# Root health check endpoint
@app.get("/", summary="Health Check")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 