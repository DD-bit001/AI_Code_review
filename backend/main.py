from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database, models
from routers import auth_router, project_router, review_router, provider_router, chat_router

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Code Review Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(provider_router.router)
app.include_router(review_router.router)
app.include_router(chat_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to AI Code Review Assistant API"}
