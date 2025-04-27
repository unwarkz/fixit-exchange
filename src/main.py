from fastapi import FastAPI
from src.infrastructure.web.webhook_waba import router as waba_router
from src.infrastructure.web.webhook_okdesk import router as okdesk_router

app = FastAPI()
app.include_router(waba_router, prefix="/api")
app.include_router(okdesk_router, prefix="/api")
