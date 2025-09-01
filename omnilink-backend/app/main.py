from fastapi import FastAPI

app = FastAPI(title="OmniLink API")

@app.get("/health")
def health():
    return {"status": "ok"}

from app.db.session import engine, Base
from app.api.routes import router as api_router


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix="/api")
