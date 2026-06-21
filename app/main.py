from fastapi import FastAPI
from app.routes.system import router as system_router

app = FastAPI(title="Auto Grader API", version="0.1.0")

app.include_router(system_router)
