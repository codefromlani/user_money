from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from .api.routes.auth import router as auth_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Request: {request.method} {request.url} | Duration: {duration:.4f} seconds")
    return response

app.include_router(auth_router)

@app.get('/')
def home():
    return {"message": "Welcome to UserMoney"}