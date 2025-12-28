from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from core.refactors import validator_period

from utils.enums import PaymentTypeEnum, PeriodDaysEnum, OpenStatusEnum, ContractTypeEnum
from utils.date_settings import timedelta_workdays
from utils.salt_convector import from_json

class SupplierBase(BaseModel):
    name : str
    address : str
    form : str

class SupplierCreate(SupplierBase):
    pass
class SupplierUpdate(SupplierBase):
    supplier_id : int


class ContractBase(BaseModel):
    contract_id: int = None
    contract: Optional[str]
    contract_date: Optional[date]
    contract_type : Optional[ContractTypeEnum]
    supplier_id: Optional[int]
    lifetime: date | None
    payment_type: Optional[PaymentTypeEnum] = None
    payment_date: Optional[dict] = {}
    delivery_date: Optional[dict] = {}
    open_status: Optional[OpenStatusEnum] = OpenStatusEnum.OPEN
    employee_id: int
    document: Optional[str] = None
    description : Optional[str] = None


class ContractCreate(ContractBase):
    payment1: Optional[str] = None
    payment1_type: Optional[PeriodDaysEnum] = None
    payment2: Optional[str] = None
    payment2_type: Optional[PeriodDaysEnum] = None
    delivery:Optional[str] = None
    delivery_type: Optional[PeriodDaysEnum] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calculate_payment_date(self.payment1, self.payment2)
        self.calculate_delivery_date(self.delivery)


    def calculate_payment_date(self, payment1, payment2):
        print(self.payment_type)
        match (self.payment_type):
            case PaymentTypeEnum.PREPAYMENT_100:
                self.payment_date["1"] = {}
                self.payment_date["1"]["date"] = payment1 if validator_period(payment1) else timedelta_workdays(self.contract_date, payment1, self.payment1_type)
                self.payment_date["1"]["name"] = "Предоплата"
                self.open_status = OpenStatusEnum.PAYMENT
            case PaymentTypeEnum.PARTIAL_PRE_BEFORE:
                self.payment_date["1"] = {}
                print(payment1)
                print(validator_period(payment1))
                self.payment_date["1"]["date"] = payment1 if validator_period(payment1) else timedelta_workdays(self.contract_date, payment1, self.payment1_type)
                self.payment_date["1"]["name"] = "Предоплата"
                self.payment_date["2"] = {}
                self.payment_date["2"]["date"] = payment2 if validator_period(payment2) else timedelta_workdays(self.contract_date, payment2, self.payment2_type)
                self.payment_date["2"]["name"] = "Остаток"
                self.open_status = OpenStatusEnum.PAYMENT
            case PaymentTypeEnum.PARTIAL_PRE_AFTER:
                self.payment_date["1"] = {}
                self.payment_date["1"]["date"] = payment1 if validator_period(payment1) else timedelta_workdays(self.contract_date, payment1, self.payment1_type)
                self.payment_date["1"]["name"] = "Предоплата"
                self.payment_date["2"] = {}
                self.payment_date["2"]["period"] = payment2
                self.payment_date["2"]["days"] = self.payment1_type.value
                self.payment_date["2"]["name"] = "Остаток"
                self.open_status = OpenStatusEnum.PAYMENT
            case PaymentTypeEnum.POSTPAYMENT_100:
                self.payment_date["1"] = {}
                self.payment_date["1"]["period"] = payment1
                self.payment_date["1"]["days"] = self.payment1_type.value
                self.payment_date["1"]["name"] = "Оплата"
                self.open_status = OpenStatusEnum.DELIVERY
            case _: return

    def calculate_delivery_date(self, delivery):
        match (self.payment_type):
            case PaymentTypeEnum.PREPAYMENT_100 | PaymentTypeEnum.PARTIAL_PRE_BEFORE | PaymentTypeEnum.PARTIAL_PRE_AFTER:
                self.delivery_date["1"] = {}
                self.delivery_date["1"]["period"] = delivery
                self.delivery_date["1"]["days"] = self.delivery_type.value
                self.delivery_date["1"]["name"] = "Поставка"

            case PaymentTypeEnum.POSTPAYMENT_100:
                self.delivery_date["1"] = {}
                self.delivery_date["1"]["date"] = delivery if validator_period(delivery) else timedelta_workdays(self.contract_date, delivery, self.delivery_type)
                self.delivery_date["1"]["name"] = "Поставка"
            case _: return

class ContractUpdate(ContractBase):
    first_name: str
    name : Optional[str]
    activity : Optional[bool]



class Filters(BaseModel):
    supplier_filter : list = None
    open_status_filter: Optional[OpenStatusEnum] | None = None
    activity_filter: bool = None
    employee_filter : int = None
    pay_from: date = None
    pay_to : date = None
    delivery_from : date = None
    delivery_to : date = None
    contract_from : date = None
    contract_to : date = None
    document_type : str = None


class InvoiceAndOrder(BaseModel):
    contract_id : int = None
    account_id : int = None
    specification_id : int = None
    item : str
    date : date

class CreateInvoice(InvoiceAndOrder):
    delivery : str = None

class CreateCod(InvoiceAndOrder):
    payment: str = None

class EmployeeBase(BaseModel):
    employee_id : int = None
    t_id : int = None
    first_name : str = None
    is_group : bool = False
    vacation : str = None
    login : str = None
    password: str = None
    salt : bytes = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.salt:
            self.salt = from_json(self.salt)

class EmployeeRead(BaseModel):
    login : str = None
    password : str = None

class CreateDocumentToContract(BaseModel):
    item : str = None
    contract_id : int = None
    document_date : date = None
    lifetime : date = None
    payment_type: Optional[PaymentTypeEnum] = None
    employee_id : int = None
    payment_date : Optional[dict] = {}
    delivery_date : Optional[dict] = {}
    description : str = None
    document: str = None
    open_status : Optional[OpenStatusEnum] = None

    payment1: Optional[str] = None
    payment1_type: Optional[PeriodDaysEnum] = None
    payment2: Optional[str] = None
    payment2_type: Optional[PeriodDaysEnum] = None
    delivery: Optional[str] = None
    delivery_type: Optional[PeriodDaysEnum] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calculate_payment_date(self.payment1, self.payment2)
        self.calculate_delivery_date(self.delivery)


    def calculate_payment_date(self, payment1, payment2):
        print(self.payment_type)
        match (self.payment_type):
            case PaymentTypeEnum.PREPAYMENT_100:
                self.payment_date["1"] = {}
                self.payment_date["1"]["date"] = payment1 if validator_period(payment1) else timedelta_workdays(self.document_date, payment1, self.payment1_type)
                self.payment_date["1"]["name"] = "Предоплата"
                self.open_status = OpenStatusEnum.PAYMENT
            case PaymentTypeEnum.PARTIAL_PRE_BEFORE:
                self.payment_date["1"] = {}
                print(payment1)
                print(validator_period(payment1))
                self.payment_date["1"]["date"] = payment1 if validator_period(payment1) else timedelta_workdays(self.document_date, payment1, self.payment1_type)
                self.payment_date["1"]["name"] = "Предоплата"
                self.payment_date["2"] = {}
                self.payment_date["2"]["date"] = payment2 if validator_period(payment2) else timedelta_workdays(self.document_date, payment2, self.payment2_type)
                self.payment_date["2"]["name"] = "Остаток"
                self.open_status = OpenStatusEnum.PAYMENT
            case PaymentTypeEnum.PARTIAL_PRE_AFTER:
                self.payment_date["1"] = {}
                self.payment_date["1"]["date"] = payment1 if validator_period(payment1) else timedelta_workdays(self.document_date, payment1, self.payment1_type)
                self.payment_date["1"]["name"] = "Предоплата"
                self.payment_date["2"] = {}
                self.payment_date["2"]["period"] = payment2
                self.payment_date["2"]["days"] = self.payment1_type.value
                self.payment_date["2"]["name"] = "Остаток"
                self.open_status = OpenStatusEnum.PAYMENT
            case PaymentTypeEnum.POSTPAYMENT_100:
                self.payment_date["1"] = {}
                self.payment_date["1"]["period"] = payment1
                self.payment_date["1"]["days"] = self.payment1_type.value
                self.payment_date["1"]["name"] = "Оплата"
                self.open_status = OpenStatusEnum.DELIVERY
            case _: return

    def calculate_delivery_date(self, delivery):
        match (self.payment_type):
            case PaymentTypeEnum.PREPAYMENT_100 | PaymentTypeEnum.PARTIAL_PRE_BEFORE | PaymentTypeEnum.PARTIAL_PRE_AFTER:
                self.delivery_date["1"] = {}
                self.delivery_date["1"]["period"] = delivery
                self.delivery_date["1"]["days"] = self.delivery_type.value
                self.delivery_date["1"]["name"] = "Поставка"

            case PaymentTypeEnum.POSTPAYMENT_100:
                self.delivery_date["1"] = {}
                self.delivery_date["1"]["date"] = delivery if validator_period(delivery) else timedelta_workdays(self.document_date, delivery, self.delivery_type)
                self.delivery_date["1"]["name"] = "Поставка"
            case _: return





