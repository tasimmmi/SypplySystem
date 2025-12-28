from sqlalchemy import select, and_, update, or_, delete, asc, cast,\
    desc, case, column, literal, union_all
from sqlalchemy.exc import SQLAlchemyError
from telethon.tl.types.contacts import Contacts

from core.config import settings
from core.models import *
from core.schems import SupplierCreate, SupplierUpdate, Filters, ContractUpdate, ContractCreate, InvoiceAndOrder, \
    EmployeeBase, CreateDocumentToContract
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from utils.status_settings import check_account_status
from utils.date_settings import check_date_periods
import datetime

import logging

logger = logging.getLogger(__name__)
class DataBase:
    def __init__(self):
        self.connect = settings.db_url
        self.async_engine = create_async_engine(self.connect, echo=True)
        self.Session = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False
        )

    async def create_db(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def check_connection(self) -> bool:
        try:
            async with self.async_engine.begin() as conn:
                await conn.execute(text('SELECT version()'))
                return True
        except SQLAlchemyError as e:
            print(f'Error database connection: {e}')
            return False


    ### SUPPLIERS
#new
    async def get_suppliers(self):
        async with self.Session() as session:
            suppliers_query = select(Suppliers.supplier_id, Suppliers.name, Suppliers.address, Suppliers.form).order_by(Suppliers.name)
            result = await session.execute(suppliers_query)
            suppliers = result.mappings().all()
            return suppliers
#new
    async def check_supplier_name(self, name:str) -> bool:
        async with self.Session() as session :
            result = await session.scalar(select(Suppliers).where(Suppliers.name == name))
            return True if result else False

    # not use
    async def create_supplier(self, supplier_create: SupplierCreate) -> Suppliers: #создает контрагента
        supplier = Suppliers(**supplier_create.model_dump())
        async with self.Session() as session :
            session.add(supplier)
            await session.commit()
        return supplier

    # not use
    async def get_supplier(self, _id: int) -> Suppliers: #
        async with self.Session() as session:
            stmt = select(Suppliers).where(Suppliers.supplier_id == _id)
            result = await session.scalar(stmt)
            return result

    # not use
    async def update_supplier(self, supplier_update : SupplierUpdate) :
        async with self.Session() as session:
            query = update(Suppliers).where(Suppliers.supplier_id == supplier_update.supplier_id).values(name=supplier_update.name,
                                                                                                form = supplier_update.form,
                                                                                                address = supplier_update.address)
            await session.execute(query)
            await session.commit()


    ### CONTRACTS

    # new
    async def get_contracts(self):
        async with self.Session() as session:
            query = (select(
                Contracts.contract_id,
                Contracts.contract,
                Contracts.supplier_id,
                Suppliers.name,
                Contracts.contract_date,
                Contracts.contract_type,
                Contracts.activity,
                Employees.first_name,
                Contracts.description
            )
            .join(Suppliers, Contracts.supplier_id==Suppliers.supplier_id, isouter=True)
            .join(Employees, Contracts.employee_id==Employees.employee_id, isouter=True)
            .order_by(
                desc(Contracts.contract_date),
            asc(Contracts.activity),
                asc(Contracts.contract)
            ))
            result = await session.execute(query)
            contracts = result.mappings().all()
            return contracts


# new
    async def get_contract(self, _id: int) :
        async with self.Session() as session:
            query = (select(Contracts.contract_id,
                            Contracts.contract,
                            Contracts.supplier_id,
                            Suppliers.name,
                            Contracts.contract_date,
                            Contracts.contract_type,
                            Contracts.lifetime,
                            Contracts.activity,
                            Contracts.payment_type,
                            Contracts.payment_date,
                            Contracts.delivery_date,
                            Contracts.open_status,
                            Contracts.document,
                            Contracts.description,
                            Contracts.employee_id,
                            Employees.first_name
                            )
                     .join(Suppliers, Suppliers.supplier_id==Contracts.supplier_id, isouter=True)
                     .join(Employees, Employees.employee_id==Contracts.employee_id).where(Contracts.contract_id == _id)
            )
            result = await session.execute(query)
            contract = result.mappings().first()
            accounts_query = (select(
                literal('Счёт').label('document_type'),
                Accounts.account_id.label('document_id'),
                Accounts.account.label('document'),
                Accounts.open_status.label('open_status'),
                Accounts.payment_date,
                Accounts.delivery_date,
                Accounts.employee_id,
                Employees.first_name,
                Accounts.description,
                Accounts.account_date.label('document_date'),
                                     )
                              .join(Employees, Employees.employee_id == Accounts.employee_id, isouter=True)
                              .where(Accounts.contract_id == _id)
                              )

            specifications_query = (select(
                literal('Спецификация').label('document_type'),
                Specifications.specification_id.label('document_id'),
                Specifications.specification.label('document'),
                Specifications.open_status.label('open_status'),
                Specifications.payment_date,
                Specifications.delivery_date,
                Specifications.employee_id,
                Employees.first_name,
                Specifications.description,
                Specifications.specification_date.label('document_date'),
                )
            .join(Employees, Employees.employee_id == Specifications.employee_id, isouter=True)
            .where(Specifications.contract_id == _id)
            )

            combined_query = union_all(accounts_query, specifications_query).alias('combined_docs')
            final_query = select(combined_query).order_by(combined_query.c.document_date)

            result = await session.execute(final_query)
            documents = result.mappings().all()

            return contract, documents
#new
    async def get_suppliers_names(self):
        async with self.Session() as session:
            query = select(Suppliers.supplier_id, Suppliers.name).order_by(Suppliers.name).distinct()
            result = await session.execute(query)
            return result.mappings().all()
#new
    async def update_contract(self, contract: ContractUpdate):
        async with self.Session() as session:
            query = (update(Contracts).where(Contracts.contract_id == contract.contract_id).values(contract=contract.contract,
                                                                                                   supplier_id=contract.supplier_id,
                                                                                                   contract_date=contract.contract_date,
                                                                                                   contract_type = contract.contract_type,
                                                                                                   lifetime=contract.lifetime,
                                                                                                   payment_type=contract.payment_type,
                                                                                                   payment_date=contract.payment_date,
                                                                                                   delivery_date=contract.delivery_date,
                                                                                                   open_status=contract.open_status,
                                                                                                   employee_id=contract.employee_id,
                                                                                                   document=contract.document,
                                                                                                   description = contract.description,
                                                                                                   activity=contract.activity
                                                                                                   ))
            await session.execute(query)
            await session.commit()
#new
    async def check_contract_name(self, contract:str, supplier: str) -> bool:
        async with self.Session() as session :
            result = await session.scalar(select(Contracts).where(Contracts.contract == contract,
                                                                  Contracts.supplier_id == supplier))
            return True if result else False
#new
    async def create_contract(self, _create: ContractCreate) -> Contracts: #создает контрагента
        print(_create)
        async with self.Session() as session :
            result = Contracts(**_create.model_dump(exclude={'payment1', 'payment1_type', 'payment2', 'payment2_type', 'delivery', 'delivery_type'}))
            session.add(result)
            await session.commit()
        return result

    ### C.O.D
    #new
    async def create_cod(self, _create : InvoiceAndOrder, key, _dict) -> Cod:
        async with self.Session() as session:
            async with session.begin():
                query = Cod(**_create.model_dump())
                session.add(query)
                await session.flush()
                print(_dict)
                _dict['close'] = query.cod_id
                if _create.account_id:
                    stmt = update(Accounts).where(Accounts.account_id==_create.account_id,
                                           Accounts.payment_date.isnot(None)).values(
                        payment_date=func.jsonb_set(
                            Accounts.payment_date,
                            [key],  # Явно указываем тип
                            cast(_dict, JSONB),  # Явно указываем тип
                            cast(True, Boolean)
                        ))
                    select_stmt = select(Accounts).where(Accounts.account_id == _create.account_id)
                    update_stmt = update(Accounts).where(Accounts.account_id == _create.account_id)
                elif _create.specification_id:
                    stmt = update(Specifications).where(Specifications.specification_id==_create.specification_id,
                                           Specifications.payment_date.isnot(None)).values(
                        payment_date=func.jsonb_set(
                            Specifications.payment_date,
                            [key],  # Явно указываем тип
                            cast(_dict, JSONB),  # Явно указываем тип
                            cast(True, Boolean)
                        ))
                    select_stmt = select(Specifications).where(Specifications.specification_id == _create.specification_id)
                    update_stmt = update(Specifications).where(Specifications.specification_id == _create.specification_id)
                elif _create.contract_id:
                    stmt = update(Contracts).where(Contracts.contract_id == _create.contract_id,
                                           Contracts.payment_date.isnot(None)).values(
                        payment_date=func.jsonb_set(
                            Contracts.payment_date,
                            [key],  # Явно указываем тип
                            cast(_dict, JSONB),  # Явно указываем тип
                            cast(True, Boolean)
                        ))
                    select_stmt = select(Contracts).where(Contracts.contract_id == _create.contract_id)
                    update_stmt = update(Contracts).where(Contracts.contract_id == _create.contract_id)
                await session.execute(stmt)
                result = await session.execute(select_stmt)
                element = result.scalar_one_or_none()
                if element:
                    print(element.payment_type)
                    status = check_account_status(element)
                    print(status)
                    pay_date, dev_date = check_date_periods(element, status)
                    values_dict = {
                        'open_status': status,
                        'payment_date': pay_date,
                        'delivery_date': dev_date
                    }
                    await session.execute(update_stmt.values(values_dict))
            return query
    #!
    async def check_cod_parents(self, _create : InvoiceAndOrder) :
        async with self.Session() as session :
            if all ([_create.account_id, _create.account_id, _create.specification_id]) is None:
                return False
            if _create.account_id:
                payment_date = await session.scalar(select(Accounts.payment_date).where(Accounts.account_id == _create.account_id,
                                                                             Accounts.payment_date.isnot(None)))
            elif _create.specification_id:
                payment_date = await session.scalar(select(Specifications.payment_date).where(Specifications.specification_id == _create.specification_id,
                                                                             Specifications.payment_date.isnot(None)))
            elif _create.contract_id:
                payment_date = await session.scalar(select(Contracts.payment_date).where(Contracts.contract_id == _create.contract_id,
                                                                Contracts.payment_date.isnot(None)))
            #
            if isinstance(payment_date, dict):
                for key, value in payment_date.items():
                    if isinstance(value, dict):
                        if value.get('close'):
                            continue
                        return key, value

            return False, False

    # not use
    async def get_cod(self, _id : int):
        async with self.Session() as session :
            query = select(Cod).where(Cod.cod_id==_id)
            result = await session.scalar(query)
            return result

    ### INVOICE
    #!
    async def create_invoice(self, _create: InvoiceAndOrder, key, _dict) -> Invoices: #refactor
        async with self.Session() as session:
            async with session.begin():
                query = Invoices(**_create.model_dump())
                session.add(query)
                await session.flush()
                _dict['close'] = query.invoice_id
                print(_dict)

                if _create.account_id:
                    stmt = update(Accounts).where(Accounts.account_id == _create.account_id,
                                                  Accounts.delivery_date.isnot(None)).values(
                        delivery_date=func.jsonb_set(
                            Accounts.delivery_date,
                            [key],
                            cast(_dict, JSONB),
                            cast(True, Boolean)
                        ))
                    select_stmt = select(Accounts).where(Accounts.account_id == _create.account_id)
                    update_stmt = update(Accounts).where(Accounts.account_id == _create.account_id)

                elif _create.specification_id:
                    stmt = update(Specifications).where(Specifications.specification_id==_create.specification_id,Specifications.payment_date.isnot(None)).values(
                        payment_date=func.jsonb_set(
                            Specifications.payment_date,
                            [key],  # Явно указываем тип
                            cast(_dict, JSONB),  # Явно указываем тип
                            cast(True, Boolean)
                        ))
                    select_stmt = select(Specifications).where(Specifications.specification_id == _create.specification_id)
                    update_stmt = update(Specifications).where(Specifications.specification_id == _create.specification_id)

                elif _create.contract_id:
                    stmt = update(Contracts).where(Contracts.contract_id == _create.contract_id,
                                                   Contracts.delivery_date.isnot(None)).values(
                        delivery_date=func.jsonb_set(
                            Contracts.delivery_date,
                            [key],
                            cast(_dict, JSONB),
                            cast(True, Boolean)
                        ))
                    select_stmt = select(Contracts).where(Contracts.contract_id == _create.contract_id)
                    update_stmt = update(Contracts).where(Contracts.contract_id == _create.contract_id)

                await session.execute(stmt)
                result = await session.execute(select_stmt)
                element = result.scalar_one_or_none()
                if element:
                    print(element.payment_type)
                    status = check_account_status(element)
                    print(status)
                    pay_date, dev_date = check_date_periods(element, status)
                    values_dict = {
                        'open_status': status,
                        'payment_date': pay_date,
                        'delivery_date': dev_date
                    }
                    await session.execute(update_stmt.values(values_dict))
            return query
    #!
    async def check_invoice_parents(self, _create: InvoiceAndOrder):
        async with self.Session() as session:
            if all([_create.account_id, _create.account_id]) is None:
                return False
            if _create.account_id:
                delivery_date = await session.scalar(
                    select(Accounts.delivery_date).where(Accounts.account_id == _create.account_id,
                                           Accounts.delivery_date.isnot(None)))
            elif _create.specification_id:
                delivery_date = await session.scalar(select(Specifications.delivery_date).where(
                    Specifications.specification_id == _create.specification_id,
                    Specifications.delivery_date.isnot(None)))
            elif _create.contract_id:
                delivery_date = await session.scalar(
                    select(Contracts.delivery_date).where(Contracts.contract_id == _create.contract_id,
                                            Contracts.delivery_date.isnot(None)))

            if isinstance(delivery_date, dict):
                for key, value in delivery_date.items():
                    if isinstance(value, dict):
                        if value.get('close'):
                            continue
                        return key, value

            return False, False

    # not use
    async def get_invoice(self, _id : int):
        async with self.Session() as session :
            query = select(Invoices).where(Invoices.invoice_id==_id)
            result = await session.scalar(query)
            return result

    #use
    ### LOGIN PK

    async def check_user(self, login:str):
        async with self.Session() as session :
            result = await session.scalar(select(Employees).where(Employees.login == login))
            return result

    async def check_password(self, login:str, password:str):
        async with self.Session() as session :
            result = await session.scalar(select(Employees).where(Employees.login == login, Employees.password == password))
            return result









    ### --- TELEGRAM BOT --- ###

    ### PAYMENTS

    async def get_payments(self):
        async with self.Session() as session:  # Note: Session() instead of Session
            # contracts
            c_subquery = (
                select(True)
                .select_from(func.jsonb_each(Contracts.payment_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            c_query = select(
                literal('Договор').label('type'),
                Contracts.contract.label('document'),
                Suppliers.name.label('supplier_name'),
                literal(None).label('parent'),
                Contracts.payment_date,
                Employees.first_name
            ).join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id
                   ).join(Employees, Contracts.employee_id == Employees.employee_id
                          ).where(and_(Contracts.open_status == OpenStatusEnum.PAYMENT, c_subquery.exists()))

            a_subquery = (
                select(True)
                .select_from(func.jsonb_each(Accounts.payment_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < datetime.date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            a_query = (
                select(
                    literal('Счёт').label('type'),
                    Accounts.account.label('document'),
                    Suppliers.name.label('supplier_name'),
                    Contracts.contract.label('parent'),
                    Accounts.payment_date,
                    Employees.first_name
                ).select_from(Accounts)
                .outerjoin(Contracts, Contracts.contract_id == Accounts.contract_id)
                .outerjoin(
                    Suppliers,
                    case(
                        (Contracts.contract_id.isnot(None), Contracts.supplier_id),
                        else_=Accounts.supplier_id
                    ) == Suppliers.supplier_id
                )
                .join(Employees, Employees.employee_id == Accounts.employee_id)
                .where(
                    and_(
                        Accounts.open_status == OpenStatusEnum.PAYMENT,
                        a_subquery.exists()
                    )
                )
            )

            sp_subquery = (
                select(True)
                .select_from(func.jsonb_each(Specifications.payment_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < datetime.date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            sp_query = (
                select(
                    literal('Спецификация').label('type'),
                    Specifications.specification.label('document'),
                    Suppliers.name.label('supplier_name'),
                    Contracts.contract.label('parent'),
                    Specifications.payment_date,
                    Employees.first_name
                )
                .join(Contracts,
                      Contracts.contract_id == Specifications.contract_id)  # Fixed: should be contract_id, not contract
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees,
                      Employees.employee_id == Specifications.employee_id)  # Fixed: should be Specifications.employee_id
                .where(
                    and_(
                        Specifications.open_status == OpenStatusEnum.PAYMENT,
                        sp_subquery.exists()
                    )
                )
            )

            combined_query = union_all(c_query, a_query, sp_query).alias('combined_docs')
            final_query = select(combined_query).order_by(
                combined_query.c.payment_date)  # Fixed: payment_date instead of document_date

            result = await session.execute(final_query)
            return result.mappings().all()

    async def get_payments_user(self, id_: int):
        async with (self.Session() as session):
            c_subquery = (
                select(True)
                .select_from(func.jsonb_each(Contracts.payment_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            c_query = (
                select(literal('Договор').label('type'),
                       Contracts.contract.label('document'),
                       Suppliers.name.label('supplier_name'),
                       literal(None).label('parent'),
                       Contracts.payment_date)
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees, Contracts.employee_id == Employees.employee_id)
                .where(and_(
                Contracts.open_status == OpenStatusEnum.PAYMENT,
                c_subquery.exists(),
                Employees.t_id == id_))
            )

            a_subquery = (
                select(True)
                .select_from(func.jsonb_each(Accounts.payment_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < date.today() + datetime.timedelta(days=5)
                    )
                )
            )

            a_query = (
                select(
                    literal('Счёт').label('type'),
                    Accounts.account.label('document'),
                    Suppliers.name.label('supplier_name'),
                    Contracts.contract.label('parent'),
                    Accounts.payment_date  # Убрано дублирование supplier_name
                ).select_from(Accounts)
                .outerjoin(
                    Contracts,
                    Contracts.contract_id == Accounts.contract_id  # Связь по contract_id
                )
                .outerjoin(
                    Suppliers,
                        case(
                            (Contracts.contract_id.isnot(None), Contracts.supplier_id),
                            else_=Accounts.supplier_id
                        ) == Suppliers.supplier_id

                )
                .join(Employees, Employees.employee_id==Accounts.employee_id)
                .where(
                    and_(
                        Accounts.open_status == OpenStatusEnum.PAYMENT,
                        a_subquery.exists(),
                        Employees.t_id == id_  # Добавлено условие фильтрации
                    )
                )
            )

            sp_subquery = (
                select(True)
                .select_from(func.jsonb_each(Specifications.payment_date).alias('items'))
                .where(
                    and_(
                        # Проверяем наличие поля date в JSONB
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        # Сравниваем даты (дата из JSON меньше чем сегодня + 5 дней)
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < datetime.date.today() + datetime.timedelta(days=5)
                    )
                )
            )

            sp_query = (
                select(
                    literal('Спецификация').label('type'),  # Тип документа
                    Specifications.specification.label('document'),  # Номер спецификации
                    Suppliers.name.label('supplier_name'),  # Наименование поставщика
                    Contracts.contract.label('parent'),  # Родительский договор
                    Specifications.payment_date  # Данные о платежах
                )
                .join(Contracts, Contracts.contract_id == Specifications.contract_id)
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees, Specifications.employee_id == Employees.employee_id
                      )
                .where(
                    and_(
                        Specifications.open_status == OpenStatusEnum.PAYMENT,  # Статус оплаты
                        sp_subquery.exists(),  # Проверяем наличие подходящих дат платежей
                        Employees.t_id == id_  # Добавлено условие фильтрации
                    )
                )
            )

            combined_query = union_all(c_query, a_query, sp_query).alias('combined_docs')
            final_query = select(combined_query)

            result = await session.execute(final_query)
            return result.mappings().all()

    ### DELIVERY

    async def get_deliveries(self):
        async with self.Session() as session:
            # Subquery for Contracts
            c_subquery = (
                select(True)
                .select_from(func.jsonb_each(Contracts.delivery_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < datetime.date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            c_query = (
                select(
                    literal('Договор').label('type'),
                    Contracts.contract.label('document'),
                    Suppliers.name.label('supplier_name'),
                    literal(None).label('parent'),
                    Contracts.delivery_date,  # Заменено на delivery_date
                    Employees.first_name
                )
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees, Contracts.employee_id == Employees.employee_id)
                .where(and_(
                    Contracts.open_status == OpenStatusEnum.DELIVERY,  # Заменено на DELIVERY
                    c_subquery.exists()
                ))
            )

            # Subquery for Accounts
            a_subquery = (
                select(True)
                .select_from(func.jsonb_each(Accounts.delivery_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < datetime.date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            a_query = (
                select(
                    literal('Счёт').label('type'),
                    Accounts.account.label('document'),
                    Suppliers.name.label('supplier_name'),
                    Contracts.contract.label('parent'),
                    Accounts.delivery_date,  # Заменено на delivery_date
                    Employees.first_name
                )
                .select_from(Accounts)
                .outerjoin(Contracts, Contracts.contract_id == Accounts.contract_id)
                .outerjoin(
                    Suppliers,
                    case(
                        (Contracts.contract_id.isnot(None), Contracts.supplier_id),
                        else_=Accounts.supplier_id
                    ) == Suppliers.supplier_id
                )
                .join(Employees, Employees.employee_id == Accounts.employee_id)
                .where(
                    and_(
                        Accounts.open_status == OpenStatusEnum.DELIVERY,  # Заменено на DELIVERY
                        a_subquery.exists()
                    )
                )
            )

            # Subquery for Specifications
            sp_subquery = (
                select(True)
                .select_from(func.jsonb_each(Specifications.delivery_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < datetime.date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            sp_query = (
                select(
                    literal('Спецификация').label('type'),
                    Specifications.specification.label('document'),
                    Suppliers.name.label('supplier_name'),
                    Contracts.contract.label('parent'),
                    Specifications.delivery_date,  # Заменено на delivery_date
                    Employees.first_name
                )
                .join(Contracts, Contracts.contract_id == Specifications.contract_id)
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees, Employees.employee_id == Specifications.employee_id)
                .where(
                    and_(
                        Specifications.open_status == OpenStatusEnum.DELIVERY,  # Заменено на DELIVERY
                        sp_subquery.exists()
                    )
                )
            )

            # Combine queries
            combined_query = union_all(c_query, a_query, sp_query).alias('combined_docs')
            final_query = select(combined_query).order_by(
                combined_query.c.delivery_date  # Заменено на delivery_date
            )

            result = await session.execute(final_query)
            return result.mappings().all()

    async def get_deliveries_user(self, id_: int):
        async with self.Session() as session:
            c_subquery = (
                select(True)
                .select_from(func.jsonb_each(Contracts.delivery_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < date.today() + datetime.timedelta(days=5)
                    )
                )
            )
            c_query = (
                select(
                    literal('Договор').label('type'),
                    Contracts.contract.label('document'),
                    Suppliers.name.label('supplier_name'),
                    literal(None).label('parent'),
                    Contracts.delivery_date
                )
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees, Contracts.employee_id == Employees.employee_id)
                .where(
                    and_(
                        Contracts.open_status == OpenStatusEnum.DELIVERY,
                        c_subquery.exists(),
                        Employees.t_id == id_
                    )
                )
            )

            a_subquery = (
                select(True)
                .select_from(func.jsonb_each(Accounts.delivery_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < date.today() + datetime.timedelta(days=5)
                    )
                )
            )

            a_query = (
                select(
                    literal('Счёт').label('type'),
                    Accounts.account.label('document'),
                    Suppliers.name.label('supplier_name'),
                    Contracts.contract.label('parent'),
                    Accounts.delivery_date
                )
                .select_from(Accounts)
                .outerjoin(
                    Contracts,
                    Contracts.contract_id == Accounts.contract_id  # Связь по contract_id
                )
                .outerjoin(
                    Suppliers,
                    case(
                        (Contracts.contract_id.isnot(None), Contracts.supplier_id),
                        else_=Accounts.supplier_id
                    ) == Suppliers.supplier_id
                )
                .join(Employees, Employees.employee_id == Accounts.employee_id)
                .where(
                    and_(
                        Accounts.open_status == OpenStatusEnum.DELIVERY,
                        a_subquery.exists(),
                        Employees.t_id == id_  # Добавлено условие фильтрации
                    )
                )
            )

            sp_subquery = (
                select(True)
                .select_from(func.jsonb_each(Specifications.delivery_date).alias('items'))
                .where(
                    and_(
                        func.jsonb_extract_path_text(column('value'), 'date').isnot(None),
                        func.to_date(
                            func.jsonb_extract_path_text(column('value'), 'date'),
                            'YYYY-MM-DD'
                        ) < date.today() + datetime.timedelta(days=5)
                    )
                )
            )

            sp_query = (
                select(
                    literal('Спецификация').label('type'),  # Тип документа
                    Specifications.specification.label('document'),  # Номер спецификации
                    Suppliers.name.label('supplier_name'),  # Наименование поставщика
                    Contracts.contract.label('parent'),  # Родительский договор
                    Specifications.delivery_date  # Данные о доставках
                )
                .join(Contracts, Contracts.contract_id == Specifications.contract_id)
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id)
                .join(Employees, Specifications.employee_id == Employees.employee_id)
                .where(
                    and_(
                        Specifications.open_status == OpenStatusEnum.DELIVERY,  # Статус доставки
                        sp_subquery.exists(),  # Проверяем наличие подходящих дат доставок
                        Employees.t_id == id_  # Добавлено условие фильтрации
                    )
                )
            )

            combined_query = union_all(c_query, a_query, sp_query).alias('combined_docs')
            final_query = select(combined_query)

            result = await session.execute(final_query)
            return result.mappings().all()

    #LOGIN

    async def check_employee(self, t_id_ : int ):
        async with self.Session() as session:
            result = await session.execute(select(Employees.employee_id).where(Employees.t_id == t_id_))
            employee = result.scalar_one_or_none()
            print(employee)
            if employee is None:
                return True
            return False

    async def check_employee_access(self, t_id_ : int ):
        async with self.Session() as session:
            result = await session.execute(select(Employees.employee_id).where(and_(Employees.t_id == t_id_,Employees.is_group)))
            employee = result.scalar_one_or_none()
            if employee is  not None:
                return True
            return False

    async def create_employee(self, employee: EmployeeBase):
        async with self.Session() as session:
            print("Работает" + str(employee))
            employee = Employees(**employee.model_dump())
            session.add(employee)
            await session.commit()
            return employee

    async def recreate_employee(self, t_id_ : int ):
        async with self.Session() as session:
            query = update(Employees).where(Employees.t_id == t_id_).values(is_group=True)
            result = await session.execute(query)
            await session.commit()  # Не забудьте закоммитить изменения
            print(f"Обновлено строк: {result.rowcount}")

    async def start_employee(self, employee: EmployeeBase):
        async with self.Session() as session:
            async with session.begin():
                count = await session.scalar(select(Employees.employee_id).where(Employees.t_id == employee.t_id))

                query = update(Employees).where(and_(Employees.t_id == employee.t_id, Employees.is_group == True)).values(
                    login=employee.login+str(count),
                    password=employee.password,
                    salt=employee.salt

                )
                result = await session.execute(query)
                updated_user = await session.scalar(
                    select(Employees).where(and_(Employees.t_id == employee.t_id, Employees.is_group == True))
                )

                return updated_user.login if updated_user else None

    async def get_employee(self, employee: EmployeeBase):
        async with self.Session() as session:
            query = select(Employees).where(Employees.employee_id==employee.employee_id)
            result = await session.execute(query)
            if result is None:
                return None
            users = [
                {
                    "employee_id": row[0],
                    "t_id": row[1],
                    "first_name": row[2],
                    "is_group": row[3],
                    "vacation": row[4],
                    "login": row[5],
                    "password": row[6],
                    "salt": row[7]
                }
                for row in result
            ]
            return users

    async def  exit_employee(self, t_id_: int):
        async with self.Session() as session:
            query = update(Employees).where(Employees.t_id==t_id_).values(is_group=False)
            result = await session.execute(query)
            await session.commit()  # Не забудьте закоммитить изменения
            print(f"Обновлено строк: {result.rowcount}")









#new
    async def get_main(self):
        async with self.Session() as session:  # ← ВАЖНО: вызываем как функцию!

                logger.info("Getting main page data")

                # Получаем поставщиков
                suppliers_query = select(Suppliers.supplier_id, Suppliers.name)
                suppliers_result = await session.execute(suppliers_query)
                suppliers = suppliers_result.mappings().all()

                # Получаем контракты
                contracts_query = select(Contracts.contract_id, Contracts.supplier_id, Contracts.contract,
                                         Contracts.contract_type.label('type'), Contracts.lifetime)
                contracts_result = await session.execute(contracts_query)
                contracts = contracts_result.mappings().all()

                # Получаем аккаунты
                accounts_query = (
                select(Accounts.account_id, Accounts.account, Accounts.contract_id, Accounts.supplier_id,
                       Accounts.open_status,
                       case(
                           (Accounts.open_status == OpenStatusEnum.PAYMENT,
                            Accounts.payment_date),
                           (Accounts.open_status == OpenStatusEnum.DELIVERY,
                            Accounts.delivery_date),
                           else_=None
                       ).label('date'),
                       Employees.first_name, Accounts.description).join(
                    Employees, Employees.employee_id == Accounts.employee_id, isouter=True)
                )
                accounts_result = await session.execute(accounts_query)
                accounts = accounts_result.mappings().all()

                specification_query = (
                select(Specifications.specification_id, Specifications.specification, Specifications.contract_id,
                       Specifications.open_status, case(
                                             (Specifications.open_status == OpenStatusEnum.PAYMENT,
                                              Specifications.payment_date),
                                             (Specifications.open_status == OpenStatusEnum.DELIVERY,
                                              Specifications.delivery_date),
                                             else_=None
                                         ).label('date'),
                       Employees.first_name, Specifications.description).join(
                    Employees, Employees.employee_id == Specifications.employee_id, isouter=True)
                )
                specification_result = await session.execute(specification_query)
                specifications = specification_result.mappings().all()
                [print(s) for s in accounts]

                logger.info(f"Found {len(suppliers)} suppliers, {len(contracts)} contracts, {len(accounts)} accounts, {len(specifications)} specifications")

                return suppliers, contracts, accounts, specifications
#new
    async def filter_main(self, credentials : Filters):
        async with self.Session() as session:

            print(credentials)

            sup_condition = [] # supplier condition
            c_condition = [] # contract condition
            ac_condition = [] # accounts conditions
            sp_condition = [] # specification conditions

            if credentials.supplier_filter is not None:
                sup_condition.append(Suppliers.supplier_id.in_(credentials.supplier_filter))
                c_condition.append(Contracts.supplier_id.in_(credentials.supplier_filter))
                # ac_condition.append(or_(Accounts.supplier_id.in_(credentials.supplier_filter),
                #                         Contracts.supplier_id.in_(credentials.supplier_filter)))
                sp_condition.append(Contracts.supplier_id.in_(credentials.supplier_filter))

            if credentials.open_status_filter is not None:
                c_condition.append(Contracts.open_status==credentials.open_status_filter)
                ac_condition.append(Accounts.open_status==credentials.open_status_filter)
                sp_condition.append(Specifications.open_status==credentials.open_status_filter)

            if credentials.activity_filter is not None:
                c_condition.append(Contracts.contract==credentials.activity_filter)
                ac_condition.append(Accounts.account==credentials.activity_filter)
                sp_condition.append(Specifications.specification==credentials.activity_filter)

            if credentials.employee_filter is not None:
                c_condition.append(Contracts.employee_id==credentials.employee_filter)
                ac_condition.append(Accounts.employee_id==credentials.employee_filter)
                sp_condition.append(Specifications.specification==credentials.employee_filter)

            if credentials.contract_from is not None:
                c_condition.append(Contracts.contract_date>=credentials.contract_from)
                ac_condition.append(Accounts.account_date>=credentials.contract_from)
                sp_condition.append(Specifications.specification_date>=credentials.contract_from)

            if credentials.contract_to is not None:
                c_condition.append(Contracts.contract_date<=credentials.contract_to)
                ac_condition.append(Accounts.account_date<=credentials.contract_to)
                sp_condition.append(Specifications.specification_date<=credentials.contract_to)

            if credentials.pay_from is not None:
                    condition = text("""
                            contracts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.pay_from)
                    c_condition.append(condition)
                    condition = text("""
                            accounts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.pay_from)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.payment_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.payment_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                                )
                            """).bindparams(_date=credentials.pay_from)
                    sp_condition.append(condition)

            if credentials.pay_to is not None:
                    condition = text("""
                            contracts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.pay_to)
                    c_condition.append(condition)
                    condition = text("""
                            accounts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.pay_to)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.payment_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.payment_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                                )
                            """).bindparams(_date=credentials.pay_to)
                    sp_condition.append(condition)

            if credentials.delivery_from is not None:
                    condition = text("""
                            contracts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.delivery_from)
                    c_condition.append(condition)
                    condition = text("""
                            accounts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.delivery_from)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.delivery_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.delivery_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                                )
                            """).bindparams(_date=credentials.delivery_from)
                    sp_condition.append(condition)

            if credentials.delivery_to is not None:
                    condition = text("""
                            contracts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.delivery_to)
                    c_condition.append(condition)
                    condition = text("""
                            accounts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.delivery_to)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.delivery_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.delivery_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                                )
                            """).bindparams(_date=credentials.delivery_to)
                    sp_condition.append(condition)

            # Получаем поставщиков
            suppliers_query = select(Suppliers.supplier_id, Suppliers.name)
            if sup_condition:
                suppliers_query=suppliers_query.where(and_(*sup_condition))

            print(f"Условие {sup_condition}, запрос{suppliers_query}")
            suppliers_result = await session.execute(suppliers_query)
            suppliers = suppliers_result.mappings().all()

            # Получаем аккаунты
            accounts_query = (select(Accounts.account_id, Accounts.account, Accounts.contract_id, Accounts.supplier_id,
                                    Accounts.open_status,
                                     case(
                                         (Accounts.open_status == OpenStatusEnum.PAYMENT,
                                          Accounts.payment_date),
                                         (Accounts.open_status == OpenStatusEnum.DELIVERY,
                                          Accounts.delivery_date),
                                         else_=None
                                     ).label('date'),
                                    Employees.first_name, Accounts.description).join(
                Employees, Employees.employee_id==Accounts.employee_id, isouter=True)
            )
            if ac_condition:
                accounts_query = accounts_query.where(and_(*ac_condition))

            accounts_result = await session.execute(accounts_query)
            accounts = accounts_result.mappings().all()
            contract_ids_ac = [spec['contract_id'] for spec in accounts if spec['contract_id'] is not None]
            #
            print(f"Условие {ac_condition}, запрос{accounts_query}")

            specification_query = (
                select(Specifications.specification_id, Specifications.specification, Specifications.contract_id,
                       Specifications.open_status, case(
                        (Specifications.open_status == OpenStatusEnum.PAYMENT,
                         Specifications.payment_date),
                        (Specifications.open_status == OpenStatusEnum.DELIVERY,
                         Specifications.delivery_date),
                        else_=None
                    ).label('date'),
                       Employees.first_name, Specifications.description)
                .join(Employees, Employees.employee_id == Specifications.employee_id, isouter=True)
                .join(Contracts, Contracts.contract_id==Specifications.contract_id, isouter=True)
            )
            if sp_condition:
                specification_query=specification_query.where(and_(*sp_condition))
            specification_result = await session.execute(specification_query)
            specifications = specification_result.mappings().all()



            contract_ids_sp = [spec['contract_id'] for spec in specifications if spec['contract_id'] is not None]
            all_contract_ids = contract_ids_ac + contract_ids_sp
            unique_contract_ids = list(set(all_contract_ids))
            print(f"Условие {sp_condition}, запрос{specification_query}")
            # print(f"Индексы {unique_contract_ids}")

            # Получаем контракты
            contracts_query = select(Contracts.contract_id, Contracts.supplier_id, Contracts.contract,
                                     Contracts.contract_type.label('type'), Contracts.lifetime)
            if c_condition:
                contracts_query = contracts_query.where(or_(and_(*c_condition), Contracts.contract_id.in_(unique_contract_ids)))
            else:
                contracts_query = contracts_query.where(Contracts.contract_id.in_(unique_contract_ids))
            contracts_result = await session.execute(contracts_query)
            contracts = contracts_result.mappings().all()


            print(f"Условие {c_condition}, запрос{contracts_query}")

            [print(s) for s in accounts]
            logger.info(f"Found {len(suppliers)} suppliers, {len(contracts)} contracts, {len(accounts)} accounts, {len(specifications)} specifications")

            return suppliers, contracts, accounts, specifications
#new
    async def filter_contracts(self, credentials : Filters):
        async with self.Session() as session:
            c_condition = [] # contract condition

            if credentials.supplier_filter is not None:
                c_condition.append(Contracts.supplier_id.in_(credentials.supplier_filter))

            if credentials.open_status_filter is not None:
                c_condition.append(Contracts.open_status==credentials.open_status_filter)

            if credentials.activity_filter is not None:
                c_condition.append(Contracts.contract==credentials.activity_filter)

            if credentials.employee_filter is not None:
                c_condition.append(Contracts.employee_id==credentials.employee_filter)

            if credentials.contract_from is not None:
                c_condition.append(Contracts.contract_date>=credentials.contract_from)

            if credentials.contract_to is not None:
                c_condition.append(Contracts.contract_date<=credentials.contract_to)

            if credentials.pay_from is not None:
                    condition = text("""
                            contracts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.pay_from)
                    c_condition.append(condition)

            if credentials.pay_to is not None:
                    condition = text("""
                            contracts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.pay_to)
                    c_condition.append(condition)

            if credentials.delivery_from is not None:
                    condition = text("""
                            contracts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.delivery_from)
                    c_condition.append(condition)

            if credentials.delivery_to is not None:
                    condition = text("""
                            contracts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(contracts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.delivery_to)
                    c_condition.append(condition)

            # Получаем контракты
            contracts_query = (select(
                Contracts.contract_id,
                Contracts.contract,
                Contracts.supplier_id,
                Suppliers.name,
                Contracts.contract_date,
                Contracts.contract_type,
                Contracts.activity,
                Employees.first_name,
                Contracts.description
            )
            .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id, isouter=True)
            .join(Employees, Contracts.employee_id == Employees.employee_id, isouter=True)
            .order_by(
                desc(Contracts.contract_date),
                asc(Contracts.activity),
                asc(Contracts.contract)
            ))
            if c_condition:
                contracts_query = contracts_query.where(and_(*c_condition))
            contracts_result = await session.execute(contracts_query)
            contracts = contracts_result.mappings().all()

            logger.info(f"Found {len(contracts)} contracts")

            return contracts
#new
    async def filter_accounts_specifications(self, credentials : Filters):
        async with self.Session() as session:
            ac_condition = [] # accounts conditions
            sp_condition = [] # specification conditions
            a_query = None
            sp_query = None

            if credentials.supplier_filter is not None:
                sp_condition.append(Suppliers.supplier_id.in_(credentials['supplier_filter']))
                ac_condition.append(or_(Accounts.supplier_id.in_(credentials.supplier_filter),
                                        Contracts.supplier_id.in_(credentials.supplier_filter)))

            if credentials.open_status_filter is not None:
                ac_condition.append(Accounts.open_status==credentials.open_status_filter)
                sp_condition.append(Specifications.open_status==credentials.open_status_filter)

            if credentials.activity_filter is not None:
                ac_condition.append(Accounts.account==credentials.activity_filter)
                sp_condition.append(Specifications.specification==credentials.activity_filter)

            if credentials.employee_filter is not None:
                ac_condition.append(Accounts.employee_id==credentials.employee_filter)
                sp_condition.append(Specifications.specification==credentials.employee_filter)

            if credentials.contract_from is not None:
                ac_condition.append(Accounts.account_date>=credentials.contract_from)
                sp_condition.append(Specifications.specification_date>=credentials.contract_from)

            if credentials.contract_to is not None:
                ac_condition.append(Accounts.account_date<=credentials.contract_to)
                sp_condition.append(Specifications.specification_date<=credentials.contract_to)

            if credentials.pay_from is not None:
                    condition = text("""
                            accounts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.pay_from)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.payment_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.payment_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                                )
                            """).bindparams(_date=credentials.pay_from)
                    sp_condition.append(condition)

            if credentials.pay_to is not None:
                    condition = text("""
                            accounts.payment_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.payment_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.pay_to)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.payment_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.payment_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                                )
                            """).bindparams(_date=credentials.pay_to)
                    sp_condition.append(condition)

            if credentials.delivery_from is not None:
                    condition = text("""
                            accounts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                            )
                        """).bindparams(_date=credentials.delivery_from)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.delivery_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.delivery_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') >= :_date
                                )
                            """).bindparams(_date=credentials.delivery_from)
                    sp_condition.append(condition)

            if credentials.delivery_to is not None:
                    condition = text("""
                            accounts.delivery_date IS NOT NULL
                            AND EXISTS (
                                SELECT 1
                                FROM jsonb_each(accounts.delivery_date) AS items(key, value)
                                WHERE (value ->> 'date') IS NOT NULL
                                AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                            )
                        """).bindparams(_date=credentials.delivery_to)
                    ac_condition.append(condition)
                    condition = text("""
                                specifications.delivery_date IS NOT NULL
                                AND EXISTS (
                                    SELECT 1
                                    FROM jsonb_each(specifications.delivery_date) AS items(key, value)
                                    WHERE (value ->> 'date') IS NOT NULL
                                    AND TO_DATE(value ->> 'date', 'YYYY-MM-DD') <= :_date
                                )
                            """).bindparams(_date=credentials.delivery_to)
                    sp_condition.append(condition)

            if credentials.document_type != 'Спецификация':
                a_query = (select(
                    literal("Счет").label('type'),
                    Accounts.account_id,
                    Accounts.account,
                    Accounts.contract_id,
                    Contracts.contract,
                    Suppliers.supplier_id,
                    Suppliers.name,
                    Accounts.account_date,
                    Accounts.open_status,
                    Employees.first_name,
                    Accounts.description
                )
                .join(Contracts, Accounts.contract_id == Contracts.contract_id, isouter=True)
                .join(Suppliers, or_(
                    Accounts.supplier_id == Suppliers.supplier_id,
                    Contracts.supplier_id == Suppliers.supplier_id
                ),
                      isouter=True)
                .join(Employees, Accounts.employee_id == Employees.employee_id, isouter=True)
                .order_by(
                    desc(Accounts.account_date),
                    asc(Accounts.activity),
                    asc(Accounts.account)
                ))

                if ac_condition:
                    a_query=a_query.where(and_(*ac_condition))


            if credentials.document_type != 'Счет':

                sp_query = (select(
                    literal("Спецификация").label('type'),
                    Specifications.specification_id,
                    Specifications.specification,
                    Specifications.contract_id,
                    Contracts.contract,
                    Suppliers.supplier_id,
                    Suppliers.name,
                    Specifications.specification_date,
                    Specifications.open_status,
                    Employees.first_name,
                    Specifications.description
                )
                .join(Contracts, Specifications.contract_id == Contracts.contract_id, isouter=True)
                .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id, isouter=True)
                .join(Employees, Specifications.employee_id == Employees.employee_id, isouter=True)
                .order_by(
                    desc(Specifications.specification_date),
                    asc(Specifications.activity),
                    asc(Specifications.specification)
                ))
                if sp_condition:
                    sp_query = sp_query.where(and_(*sp_condition))

            if a_query is not None and sp_query is not None:
                query = union_all(a_query, sp_query)
            else:
                query = a_query if a_query is not None else sp_query
            print(query)
            result = await session.execute(query)
            return result.mappings().all()

#new
    async def create_contract_account(self, credentials : CreateDocumentToContract):
        async with self.Session() as session:
            new_account = Accounts(
                account=credentials.item,
                contract_id=credentials.contract_id,
                account_date=credentials.document_date,
                lifetime=credentials.lifetime,
                payment_type=credentials.payment_type,
                employee_id=credentials.employee_id,
                payment_date=credentials.payment_date,
                delivery_date=credentials.delivery_date,
                description=credentials.description,
                supplier_id=None,
                document=credentials.document,
            )
            new_account.open_status= check_account_status(new_account)

            session.add(new_account)
            await session.commit()
            await session.refresh(new_account)
            return new_account
#new
    async def create_contract_specification(self, credentials: CreateDocumentToContract):
        async with self.Session() as session:
            new_specification = Specifications(
                specification=credentials.item,
                contract_id=credentials.contract_id,
                specification_date=credentials.document_date,
                lifetime=credentials.lifetime,
                payment_type=credentials.payment_type,
                employee_id=credentials.employee_id,
                payment_date=credentials.payment_date,
                delivery_date=credentials.delivery_date,
                description=credentials.description,
                document=credentials.document,
            )
            new_specification.open_status = check_account_status(new_specification)

            session.add(new_specification)
            await session.commit()
            await session.refresh(new_specification)
            return new_specification


    ### ACCOUNTS

# new
    async def get_accounts_specifications(self):
        async with self.Session() as session:
            a_query = (select(
                literal("Счет").label('type'),
                Accounts.account_id,
                Accounts.account,
                Accounts.contract_id,
                Contracts.contract,
                Suppliers.supplier_id,
                Suppliers.name,
                Accounts.account_date,
                Accounts.open_status,
                Employees.first_name,
                Accounts.description
            )
            .join(Contracts, Accounts.contract_id == Contracts.contract_id, isouter=True)
            .join(Suppliers, or_(
        Accounts.supplier_id == Suppliers.supplier_id,
        Contracts.supplier_id == Suppliers.supplier_id
    ),
    isouter=True)
            .join(Employees, Accounts.employee_id == Employees.employee_id, isouter=True)
            .order_by(
                desc(Accounts.account_date),
                asc(Accounts.activity),
                asc(Accounts.account)
            ))

            sp_query = (select(
                literal("Спецификация").label('type'),
                Specifications.specification_id,
                Specifications.specification,
                Specifications.contract_id,
                Contracts.contract,
                Suppliers.supplier_id,
                Suppliers.name,
                Specifications.specification_date,
                Specifications.open_status,
                Employees.first_name,
                Specifications.description
            )
            .join(Contracts, Specifications.contract_id == Contracts.contract_id, isouter=True)
            .join(Suppliers, Contracts.supplier_id == Suppliers.supplier_id, isouter=True)
            .join(Employees, Specifications.employee_id == Employees.employee_id, isouter=True)
            .order_by(
                desc(Specifications.specification_date),
                asc(Specifications.activity),
                asc(Specifications.specification)
            ))
            query=union_all(a_query, sp_query)
            result = await session.execute(query)
            result = result.mappings().all()
            return result
#new
    async def get_account(self, _id: int):
        async with self.Session() as session:
            query = (
                select(
                    Accounts.account_id,
                    Accounts.account,
                    Accounts.account_date,
                    Suppliers.supplier_id,
                    Suppliers.name,
                    Contracts.contract,
                    Accounts.contract_id,
                    Accounts.lifetime,
                    Accounts.activity,
                    Accounts.payment_type,
                    Accounts.payment_date,
                    Accounts.delivery_date,
                    Accounts.open_status,
                    Accounts.document,
                    Accounts.description,
                    Accounts.employee_id,
                    Employees.first_name
                )
                .join(Suppliers, Suppliers.supplier_id == Contracts.supplier_id, isouter=True)
                .join(Employees, Employees.employee_id == Contracts.employee_id).
                where(Accounts.account_id == _id)
            )
            result = await session.execute(query)
            accounts = result.mappings().first()
            return accounts

db_connection = DataBase()