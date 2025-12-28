from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.exc import SQLAlchemyError

from core.db import db_connection

system_router = APIRouter(tags=['System'], prefix="/api_system")

@system_router.get('/check')
async def check_connection(response: Response):
   if await db_connection.check_connection():
       response.status_code = 200
       return {'message': 'ok'}
   else:
       response.status_code = 500
       return {'message': 'connection error'}

