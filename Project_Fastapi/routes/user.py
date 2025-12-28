from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from core.config import settings
from core.db import db_connection
from authx import AuthX, AuthXConfig

from core.schems import SupplierCreate, SupplierUpdate, ContractUpdate, Filters, ContractCreate, InvoiceAndOrder, \
    CreateCod, CreateInvoice, EmployeeRead, CreateDocumentToContract
from utils.salt_convector import to_json
from utils.enums import OpenStatusEnum

user_router = APIRouter(prefix="/api_user", tags=["Users"])

config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=settings.auth_jwt.private_key,
    JWT_TOKEN_LOCATION=['headers']
)

security = AuthX(config=config)

    ### SUPPLIERS

# not use
@user_router.post("/create_supplier")
async def create_supplier(credentials:  SupplierCreate):
    if await db_connection.check_supplier_name(credentials.name):
        raise HTTPException(status_code=400, detail="Supplier already registered")
    else:
        await db_connection.create_supplier(credentials)
        return {"message": "Supplier created successfully"}
# not use
@user_router.get('/get_supplier/{sup_id}', dependencies=[Depends(security.get_token_from_request)])
async def get_supplier(sup_id: int):
    try:
        supplier = await db_connection.get_supplier(int(sup_id))
        if supplier is None:
            raise HTTPException(status_code=404, detail="User not found")
        return jsonable_encoder(supplier)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

#not use
@user_router.post("/update_supplier/{sup_id}", dependencies=[Depends(security.get_token_from_request)])
async def update_supplier(credentials:  SupplierUpdate):
    try:
        await db_connection.update_supplier(credentials)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})


    ### CONTRACTS
#
@user_router.post("/create_contract")
async def register(credentials:  ContractCreate):
    if await db_connection.check_contract_name(credentials.contract, credentials.supplier_id):
        raise HTTPException(status_code=400, detail="Supplier already registered")
    else:
        await db_connection.create_contract(credentials)
        return {"message": "Supplier created successfully"}

# new
@user_router.get("/suppliers_names")
async def get_suppliers_names():
    try:
        result = await db_connection.get_suppliers_names()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})



### CONTRACTS
#new
@user_router.post("/update_contract")
async def update_contract(contract : ContractUpdate):
    print(contract)
    try:
        await db_connection.update_contract(contract)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})
#new
@user_router.post("/filter_contracts")
async def filter_contracts(filters : Filters):
    try:

        result = await db_connection.filter_contracts(filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})






### INVOICES


#not use
@user_router.get("/get_invoice/{_id}")
async def get_invoice(_id: int):
    try:
        result = await db_connection.get_invoice(_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

### COD


#not use
@user_router.get("/get_cod/{_id}")
async def get_cod(_id: int):
    try:
        result = await db_connection.get_cod(_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})


### LOGIN


@user_router.get("/authentication")
async def login(credentials: EmployeeRead):
    user = await db_connection.check_user(credentials.login)
    if user:
        print('1'+str(user.salt))
        salt=to_json(user.salt)
        print('2'+str(salt))
        return {'salt': salt}
    raise HTTPException(status_code=400, detail="Incorrect login")

@user_router.get("/login")
async def login(credentials: EmployeeRead):
    user = await db_connection.check_password(credentials.login, credentials.password)
    if user:
        token = security.create_access_token(uid=str(user.login))
        user_id=user.employee_id
        return {'access_token': token, 'user_id': user_id}
    raise HTTPException(status_code=400, detail="Incorrect password")

# main

@user_router.get("/main")
async def get_main():
    try:
        suppliers, contracts, accounts, specifications = await db_connection.get_main()
        return {
            "suppliers": suppliers,
            "contracts": contracts,
            "accounts": accounts,
            "specifications": specifications
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})



# CONTRACT
#new
@user_router.get("/get_contracts", dependencies=[Depends(security.get_token_from_request)])
async def get_contracts():
    try:
        contracts = await db_connection.get_contracts()
        return contracts
    except Exception as e:
            raise HTTPException(status_code = 400, detail={"message": f'Error: {str(e)}'})

@user_router.get('/get_contract/{_id}', dependencies=[Depends(security.get_token_from_request)])
async def get_contract(_id: int):
    try:
        contract, documents = await db_connection.get_contract(int(_id))
        result = []
        for document in documents:
            doc_dict = dict(document)

            if doc_dict['open_status'] == OpenStatusEnum.OPEN or doc_dict['open_status'] == OpenStatusEnum.CLOSE:
                doc_dict['status_date'] = ''

            elif doc_dict['open_status'] == OpenStatusEnum.PAYMENT:
                doc_dict['status_date'] = ''
                payment_date = doc_dict.get('payment_date')
                if payment_date and isinstance(payment_date, dict):
                    for value in payment_date.values():
                        if isinstance(value, dict) and 'date' in value:
                            doc_dict['status_date'] = value['date']
                            break

            elif doc_dict['open_status'] == OpenStatusEnum.DELIVERY:
                doc_dict['status_date'] = ''
                delivery_date = doc_dict.get('delivery_date')
                if delivery_date and isinstance(delivery_date, dict):
                    for value in delivery_date.values():
                        if isinstance(value, dict) and 'date' in value:
                            doc_dict['status_date'] = value['date']
                            break

            else:
                doc_dict['status_date'] = 'Ошибка загрузки даты'

            result.append(doc_dict)
        return {
            "contract": contract,
            "documents": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

@user_router.post("/contract/add_account")
async def add_account(credentials: CreateDocumentToContract):
    try:
        await db_connection.create_contract_account(credentials)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})

@user_router.post("/contract/add_specification")
async def add_specification(credentials: CreateDocumentToContract):
    try:
        await db_connection.create_contract_account(credentials)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})



# CODS AND INVOICES

@user_router.post("/create_cod")
async def create_cod(credentials:  InvoiceAndOrder):
    print(credentials)
    key, value = await db_connection.check_cod_parents(credentials)
    if all([key, value]) is not None:
        await db_connection.create_cod(credentials, key, value)
        return {"message": "Supplier created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Supplier already registered")

@user_router.post("/create_invoice")
async def create_invoice(credentials:  InvoiceAndOrder):
    key, value = await db_connection.check_invoice_parents(credentials)
    if all([key, value]) is not None:
        await db_connection.create_invoice(credentials, key, value)
        return {"message": "Supplier created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Supplier already registered")

#ACCOUNTS

@user_router.get("/get_accounts_specifications", dependencies=[Depends(security.get_token_from_request)])
async def get_accounts_specifications():
    try:
        accounts = await db_connection.get_accounts_specifications()
        return accounts
    except Exception as e:
            raise HTTPException(status_code = 400, detail={"message": f'Error: {str(e)}'})

@user_router.get("/get_account/{_id}", dependencies=[Depends(security.get_token_from_request)])
async def get_account(_id: int):
    try:
        account = await db_connection.get_account(int(_id))
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": f'Error: {str(e)}'})


# SUPPLIERS
@user_router.get("/get_suppliers")
async def get_suppliers():
    try:
        suppliers = await db_connection.get_suppliers()
        return suppliers
    except Exception as e:
            raise HTTPException(status_code = 400, detail={"message": f'Error: {str(e)}'})

# FILTERS

@user_router.post("/filter_main", dependencies=[Depends(security.get_token_from_request)])
async def filter_main(credentials : Filters):
    try:
        suppliers, contracts, accounts, specifications = await db_connection.filter_main(credentials)
        return {
            "suppliers": suppliers,
            "contracts": contracts,
            "accounts": accounts,
            "specifications": specifications
        }
    except Exception as e:
            raise HTTPException(status_code = 400, detail={"message": f'Error: {str(e)}'})


@user_router.post("/filter_contracts", dependencies=[Depends(security.get_token_from_request)])
async def filter_contracts(credentials : Filters):
    try:
        contracts = await db_connection.filter_contracts(credentials)
        return contracts
    except Exception as e:
            raise HTTPException(status_code = 400, detail={"message": f'Error: {str(e)}'})

@user_router.post("/filter_accounts", dependencies=[Depends(security.get_token_from_request)])
async def filter_accounts_specifications(credentials : Filters):
    try:
        contracts = await db_connection.filter_accounts_specifications(credentials)
        return contracts
    except Exception as e:
            raise HTTPException(status_code = 400, detail={"message": f'Error: {str(e)}'})


