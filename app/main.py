from fastapi import FastAPI
from app.core.middleware import AuthMiddleware
from app.utils.helpers.exception import register_exception_handlers
from app.api.v1.route_v1 import v1_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os

load_dotenv()

os.makedirs("static", exist_ok=True)

app = FastAPI(title="Rekgizi API")
app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

for router in v1_router:
    app.include_router(router, prefix="/api/v1")

register_exception_handlers(app)
