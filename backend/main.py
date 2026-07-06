
import os
from dotenv import load_dotenv

load_dotenv()

import logging

logging.basicConfig(
    filename = "logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from auth.router import router as auth_router
from chat.router import router as chat_router


Base.metadata.create_all(bind=engine)


app = FastAPI(title = "app")
app.add_middleware(
    CORSMiddleware,
    allow_origins = os.getenv("ALLOW_ORIGINS", "*"),
    allow_methods = os.getenv("ALLOW_METHODS", "*"),
    allow_headers = os.getenv("ALLOW_HEADERS", "*"),
)


app.include_router(auth_router, prefix = "/auth", tags = ["auth"])
app.include_router(chat_router, prefix = "/chat", tags = ["chat"])
