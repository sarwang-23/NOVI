from fastapi import FastAPI


app = FastAPI(
    title="Novi Backend API",
    version="1.0.0"
)




@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "Novi Backend is running"
    }
