from dotenv import load_dotenv
from fastapi import FastAPI

_ = load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return{"message": "Hello World"}