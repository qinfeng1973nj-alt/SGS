from fastapi import FastAPI
from app.routes.system import router as system_router
from app.routes.score import router as score_router

app = FastAPI(title="SGS API", version="0.1.0")

app.include_router(system_router)
app.include_router(score_router)

