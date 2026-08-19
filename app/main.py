from fastapi import FastAPI, Depends
from sqlalchemy import text

from app.database.connection import engine
from app.modules.student.router import router as student_router
from app.core.auth import auth0
from app.modules.auth.router import router as auth_router

app = FastAPI(
    title="Novi Backend API",
    version="1.0.0"
)

app.include_router(student_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "Novi Backend is running"
    }

@app.get("/api/v1/auth/me")
def me(user=Depends(auth0.get_user)):
    return user




@app.get("/health/database")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


    return {
        "success": True,
        "message": "Novi Database is connected"
    }
