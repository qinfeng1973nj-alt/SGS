from fastapi import FastAPI
from app.core.config import settings
from app.routes.system import router as system_router
from app.routes.score import router as score_router

app = FastAPI(title=settings.app_name)

app.include_router(system_router)
app.include_router(score_router)


@app.get("/system/config-status")
def config_status():
    return {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "openai_configured": bool(settings.openai_api_key),
        "openai_model": settings.openai_model,
    }
