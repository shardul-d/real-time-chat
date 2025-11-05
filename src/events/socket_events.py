from fastapi import HTTPException
import socketio
from typing import Any

from utils.auth_utils import cookie_parser

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

@sio.event
async def connect(sid: str, environ: dict[str, Any]):
  cookies = cookie_parser(environ)
  access_token = cookies.get("access_token")
  
  if not access_token:
    raise ConnectionRefusedError("Missing access token.")
  print(f"sid is {sid}")
  print(f"Received access token in connect event: {access_token}")
  