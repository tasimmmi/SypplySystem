from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from core.config import settings
from core.db import db_connection
from authx import AuthX, AuthXConfig

from core.schems import EmployeeBase
from utils.user_construct import user_construct

telegram_router = APIRouter(prefix="/api_telegram", tags=["Telegram"])

config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=settings.auth_jwt.private_key,
    JWT_TOKEN_LOCATION=['headers']
)

security = AuthX(config=config)

### PAYMENTS

@telegram_router.get("/report_payments/user/{_id}")
async def get_payments(_id):
    try:
        payments = await db_connection.get_payments_user(int(_id))
        return payments
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

@telegram_router.get("/report_payments")
async def get_payments():
    try:
        payments = await db_connection.get_payments()
        return payments
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

### DELIVERY

@telegram_router.get("/report_delivery/user/{_id}")
async def get_delivery(_id: int):
    try:
        delivery = await db_connection.get_delivery_user(int(_id))
        return delivery
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

@telegram_router.get("/report_delivery")
async def get_delivery():
    try:
        delivery = await db_connection.get_delivery()
        return delivery
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})


### LOGIN

@telegram_router.post("/create_employee")
async def create_employee(employee: EmployeeBase):
    try:
        if await db_connection.check_employee(employee.t_id):
            await db_connection.create_employee(employee)
            return  {"message": "Employee created successfully"}
        else:
            await db_connection.recreate_employee(employee.t_id)
            return {"message": "Employee recreated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

@telegram_router.post("/start_employee/{t_id}")
async def start_employee(employee: EmployeeBase):
    print(employee)
    try:
        if await db_connection.check_employee_access(employee.t_id):
            login = await db_connection.start_employee(employee)
            return {"login": login}
        else: return {"message": "Employee not found"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

@telegram_router.post("/exit_employee/{t_id}")
async def exit_employee(t_id : int):
    try:
        if await db_connection.check_employee_access(t_id):
            await db_connection.exit_employee(t_id)
            return  {"message": "Employee exit successfully"}
        return {"message": "Employee not found"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})





