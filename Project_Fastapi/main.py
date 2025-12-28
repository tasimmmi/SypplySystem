from core.config import settings
from fastapi import FastAPI
import uvicorn

from routes.system import system_router
from routes.user import user_router
from routes.telegram import telegram_router

main_app = FastAPI()
main_app.include_router(system_router)
main_app.include_router(user_router)
main_app.include_router(telegram_router)



if __name__ == "__main__":
    uvicorn.run(main_app, host=settings.host, port=settings.port)