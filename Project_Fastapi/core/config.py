from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class AuthJWT(BaseModel):

    private_key: str = os.getenv("SECRET_KEY")
    header_type: str = "token"
    algorithm: str = "RS256"


class Settings(BaseSettings):

    #start settings app
    host: str = os.getenv("HOST")
    port: int = int(os.getenv("PORT"))

    #database_settings_app
    db_host : str = os.getenv("DB_HOST")
    db_port: str = str(os.getenv("DB_PORT"))
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_name: str = os.getenv("DB_NAME")
    db_url: str = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    #jwt_setting_app
    auth_jwt: AuthJWT = AuthJWT()

settings = Settings()

