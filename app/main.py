from fastapi import FastAPI
from app.core.middleware import AuthMiddleware
from app.utils.helpers.exception import register_exception_handlers
from app.api.v1.route_v1 import v1_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import sys
print("PYTHON USED:", sys.executable)

load_dotenv()

app = FastAPI(title="Rekgizi API")
app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for router in v1_router:
    app.include_router(router, prefix="/api/v1")

register_exception_handlers(app)
