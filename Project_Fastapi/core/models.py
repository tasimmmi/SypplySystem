from sqlalchemy import String, Integer, Boolean, DateTime, CheckConstraint, ForeignKey, text, JSON, BigInteger, Enum as E, Date, Index
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from datetime import date

from utils.enums import PaymentTypeEnum, OpenStatusEnum, ContractTypeEnum

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Employees(Base):
    __tablename__ = 'employees'

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    t_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_group: Mapped[bool] = mapped_column(Boolean, nullable=False)
    vacation: Mapped[str] = mapped_column(String(100), nullable=True)
    login: Mapped[str] = mapped_column(String(25), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    salt: Mapped[bytes] = mapped_column(BYTEA, nullable=True)

    __table_args__ = (

        Index('ix_employee_t_id_first_name', 't_id', 'first_name'),
        Index('ix_employee_login', 't_id', 'login'),

    )

class Suppliers(Base):
    __tablename__ = 'suppliers'

    supplier_id: Mapped[int] = mapped_column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    form : Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)

class Contracts(Base):
    __tablename__ = 'contracts'

    contract_id : Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    contract: Mapped[str] = mapped_column(nullable=False)
    contract_type : Mapped[str] = mapped_column(E(ContractTypeEnum), nullable=False)
    contract_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('suppliers.supplier_id'), nullable=False)
    lifetime: Mapped[date] = mapped_column(Date, nullable=True)
    activity : Mapped[bool] = mapped_column(Boolean, server_default=text('TRUE'), nullable=False)

    payment_type : Mapped[PaymentTypeEnum] = mapped_column(E(PaymentTypeEnum), nullable=True)
    payment_date: Mapped[dict] = mapped_column(JSONB, nullable=True)
    delivery_date : Mapped[dict] = mapped_column(JSONB, nullable=True)
    open_status : Mapped[OpenStatusEnum] = mapped_column(E(OpenStatusEnum), nullable=True)

    description: Mapped[str] = mapped_column(String, nullable=True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('employees.employee_id'), nullable=False)
    document: Mapped[str] = mapped_column(nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Базовые индексы для внешних ключей
        Index('ix_contracts_supplier_id', 'supplier_id'),
        Index('ix_contracts_employee_id', 'employee_id'),

        Index('ix_contracts_payment_date',
              postgresql_using='gin',
              postgresql_ops={'payment_date': 'jsonb_path_ops'}),
        Index('ix_contracts_delivery_date',
              postgresql_using='gin',
              postgresql_ops={'delivery_date': 'jsonb_path_ops'}),

        Index('ix_contracts_combo_supplier', 'supplier_id', 'payment_type', 'open_status'),
        Index('ix_contracts_combo_type', 'contract_type', 'payment_type', 'open_status'),

    )


class Accounts(Base):
    __tablename__ = 'accounts'

    account_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    account: Mapped[str] = mapped_column(nullable=False)
    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('contracts.contract_id', ondelete='CASCADE'), nullable=True)
    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('suppliers.supplier_id'), nullable=True)
    account_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    lifetime: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE + INTERVAL '3 day'"), nullable=False)
    activity: Mapped[bool] = mapped_column(Boolean, server_default=text('TRUE'), nullable=False)

    payment_type : Mapped[PaymentTypeEnum] = mapped_column(E(PaymentTypeEnum), nullable=False)
    payment_date: Mapped[dict] = mapped_column(JSONB, nullable=False)
    delivery_date : Mapped[dict] = mapped_column(JSONB,nullable=False)
    open_status : Mapped[OpenStatusEnum] = mapped_column(E(OpenStatusEnum), server_default='OPEN', nullable=False)

    description : Mapped[str] = mapped_column(String, nullable=True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('employees.employee_id'), nullable=False)
    document: Mapped[str] = mapped_column(nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            'contract_id IS NOT NULL OR supplier_id IS NOT NULL',
            name='check_contract_supplier_id'
        ),

        Index('ix_accounts_contract_id', 'contract_id'),
        Index('ix_accounts_employee_id', 'employee_id'),
        Index('ix_accounts_supplier_id', 'supplier_id'),

        Index('ix_accounts_combo_contract_id', 'contract_id', 'payment_type', 'open_status'),
        Index('ix_accounts_combo_supplier_id', 'supplier_id', 'payment_type', 'open_status'),

        # Композитные индексы для частых комбинаций условий
        Index('ix_accounts_contract_status', 'contract_id', 'open_status'),
        Index('ix_accounts_date_status', 'account_date', 'open_status'),
        Index('ix_accounts_payment_status', 'payment_type', 'open_status'),

        # Индексы для JSONB полей (если часто фильтруете по внутренним полям)
        Index('ix_accounts_payment_date',
              postgresql_using='gin',
              postgresql_ops={'payment_date': 'jsonb_path_ops'}),
        Index('ix_accounts_delivery_date',
              postgresql_using='gin',
              postgresql_ops={'delivery_date': 'jsonb_path_ops'}),
    )

class Specifications(Base):
    __tablename__ = 'specifications'

    specification_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    specification: Mapped[str] = mapped_column(nullable=False)
    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('contracts.contract_id', ondelete='CASCADE'),
                                             nullable=False)
    specification_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    lifetime: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE + INTERVAL '3 day'"), nullable=False)
    activity: Mapped[bool] = mapped_column(Boolean, server_default=text('TRUE'), nullable=False)

    payment_type: Mapped[PaymentTypeEnum] = mapped_column(E(PaymentTypeEnum), nullable=False)
    payment_date: Mapped[dict] = mapped_column(JSONB, nullable=False)
    delivery_date: Mapped[dict] = mapped_column(JSONB, nullable=False)
    open_status: Mapped[OpenStatusEnum] = mapped_column(E(OpenStatusEnum), server_default='OPEN', nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('employees.employee_id'), nullable=False)
    document: Mapped[str] = mapped_column(nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(),
                                                onupdate=func.now())

    __table_args__ = (
        Index('ix_specifications_contract_id', 'contract_id'),
        Index('ix_specifications_employee_id', 'employee_id'),

        Index('ix_specifications_combo_contract_id', 'contract_id', 'payment_type', 'open_status'),

        # Композитные индексы для частых комбинаций условий
        Index('ix_specifications_contract_status', 'contract_id', 'open_status'),
        Index('ix_specifications_date_status', 'specification_date', 'open_status'),
        Index('ix_specifications_payment_status', 'payment_type', 'open_status'),

        # Индексы для JSONB полей (если часто фильтруете по внутренним полям)
        Index('ix_specifications_payment_date',
              postgresql_using='gin',
              postgresql_ops={'payment_date': 'jsonb_path_ops'}),
        Index('ix_specifications_delivery_date',
              postgresql_using='gin',
              postgresql_ops={'delivery_date': 'jsonb_path_ops'}),

        # Индексы для сортировки (если часто используете ORDER BY без фильтрации WHERE)
        Index('ix_specifications_spec_date_desc', text('specification_date DESC'))

    )

class  Cod(Base):
    __tablename__ = 'cod'

    cod_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('contracts.contract_id', ondelete='CASCADE'),
                                             nullable=True)
    account_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('accounts.account_id', ondelete='CASCADE'),
                                            nullable=True)
    specification_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('specifications.specification_id', ondelete='CASCADE'),
                                            nullable=True)
    date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    item: Mapped[str] = mapped_column(String, nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            'contract_id IS NOT NULL OR account_id IS NOT NULL OR specification_id IS NOT NULL',
            name='at_least_one_fk_not_null'
        ),
        Index('ix_cod_contract_id', 'contract_id'),
        Index('ix_cod_account_id', 'account_id'),
        Index('ix_cod_specification_id', 'specification_id'),
    )

class  Invoices(Base):
    __tablename__ = 'invoices'

    invoice_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(BigInteger,ForeignKey('contracts.contract_id', ondelete='CASCADE'), nullable=True)
    account_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=True)
    specification_id: Mapped[int] = mapped_column(BigInteger,
                                                  ForeignKey('specifications.specification_id', ondelete='CASCADE'),
                                                  nullable=True)
    date: Mapped[date] = mapped_column(Date,server_default=func.current_date(), nullable=False)
    item: Mapped[str] = mapped_column(String, nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            'contract_id IS NOT NULL OR account_id IS NOT NULL OR specification_id IS NOT NULL',
            name='at_least_one_fk_not_null'
        ),
        Index('ix_invoice_contract_id', 'contract_id'),
        Index('ix_invoice_account_id', 'account_id'),
        Index('ix_invoice_specification_id', 'specification_id'),
    )

