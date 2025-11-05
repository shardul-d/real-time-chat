from contextlib import asynccontextmanager
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from db import sessionmanager
from routers import auth, chat_manager
from core.config import config
from events.socket_events import sio

@asynccontextmanager
async def lifespan(app: FastAPI):  # pyright: ignore[reportUnusedParameter]
    yield
    if sessionmanager._engine is not None:  # pyright: ignore[reportPrivateUsage]
        await sessionmanager.close()


fast = FastAPI(lifespan=lifespan)

app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=fast)

fast.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fast.include_router(auth.router)
fast.include_router(chat_manager.router)

    
if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # The target: module_name:app_instance
        host="127.0.0.1",
        port=8000,
        reload=True,  # This enables the auto-reload feature
    )
