from enum import Enum

class PeriodDaysEnum(Enum):
    CALENDAR = 'к.д.'
    WORK = 'р.д.'

class PaymentTypeEnum(Enum):
    PREPAYMENT_100 = "Предоплата 100%"
    POSTPAYMENT_100 = "После поставки"
    PARTIAL_PRE_BEFORE = "Частичная предоплата + оплата перед поставкой"
    PARTIAL_PRE_AFTER = "Частичная предоплата + оплата после поставки"

class DeliveryStatus(Enum):
    START = 'Оформлен'
    PREPAYMENT = "Требует предоплату"
    POSTPAYMENT = "Требует оплату (товар прибыл)"
    IN_DELIVERY = "Ожидает поставку"
    SUCCESS = "Успешно завершен"

class OpenStatusEnum(Enum):
    OPEN = 'Открыт'
    PAYMENT = 'Ожидает опалату'
    DELIVERY = 'Ожидает поставку'
    CLOSE = "Закрыт"

class ContractTypeEnum(Enum):
    COMMITMENT = 'До выполнения обязательств'
    LIFETIME = 'До истечения срока'


