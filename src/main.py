from fastapi import FastAPI
import uvicorn
from routers import auth

app = FastAPI()

app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # The target: module_name:app_instance
        host="127.0.0.1",
        port=8000,
        reload=True,  # This enables the auto-reload feature
    )
