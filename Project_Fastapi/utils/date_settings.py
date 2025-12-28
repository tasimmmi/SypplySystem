from datetime import date, timedelta, datetime
from utils.enums import PeriodDaysEnum, OpenStatusEnum
from core.models import Accounts, Contracts, Specifications

holidays = [
    date(2025, 1, 1), # новый год
    date(2025, 1, 2), # 2-января
    date(2025, 1, 7), # рождество
    date(2025, 3, 8), # 8 марта
    date(2025, 5, 1), # 1 мая
    date(2025, 5, 9), # 9 мая
    date(2025, 7, 3), # 3 июля
    date(2025, 11, 7), # 7 ноября
    date(2025, 12, 25) # католическое рождество
]

def timedelta_workdays(start_date, value, days):
    value = int(value)
    if days == PeriodDaysEnum.CALENDAR or days == PeriodDaysEnum.CALENDAR.value:
        print('1: ' + str(start_date + timedelta(days=value)))
        return str(start_date + timedelta(days=value))
    elif days == PeriodDaysEnum.WORK or days == PeriodDaysEnum.WORK.value:
        current_date = start_date
        for i in range(value):
            current_date += timedelta(days=1)
            while current_date.weekday() > 5 or current_date in holidays:
                current_date += timedelta(days=1)
        print('2: ' + str(current_date.date()))
        return str(current_date.date())
    return None

def check_date_periods(element: Accounts | Contracts | Specifications, status):
    if isinstance(element, Accounts):
        start = element.account_date
    if isinstance(element, Contracts):
        start = element.contract_date
    if isinstance(element, Specifications):
        start=element.specification_date
    match status:
        case OpenStatusEnum.OPEN | OpenStatusEnum.CLOSE:
            return element.payment_date, element.delivery_date
        case OpenStatusEnum.PAYMENT:
            for key, value in element.payment_date.items():
                if 'close' in value or 'date' in value:
                    continue
                if 'period' and 'days' in value:
                    start_date =datetime.strptime(element.delivery_date['1']['date'], '%Y-%m-%d').date()  if 'date' in element.delivery_date['1'] else start
                    print('Начальная дата:' + str(start_date))
                    _period = value['period']
                    _days = value['days']
                    value['date'] = timedelta_workdays(start_date, _period, _days)
                    value.pop('period', None)
                    value.pop('days', None)
                    continue
                raise Exception('Incorrect status information with OpenStatus.PAYMENT')
        case OpenStatusEnum.DELIVERY:
            for key, value in element.delivery_date.items():
                if 'close' in value:
                    raise Exception('Incorrect status information OpenStatus.DELIVERY')
                if 'date' in value:
                    continue
                if 'period' and 'days' in value:
                    start_date = start
                    for _key, _value in element.payment_date.items():
                        if 'date' in _value and 'close' in _value:
                            start_date = datetime.strptime(_value['date'], '%Y-%m-%d').date()
                    print('Начальная дата:' + str(start_date))
                    _period = value['period']
                    _days = value['days']
                    value['date'] = timedelta_workdays(start_date, _period, _days)
                    value.pop('period', None)
                    value.pop('days', None)
                    print('Итог' + str(element.payment_date) +str(element.delivery_date))
                    continue
                raise Exception('Incorrect status information with OpenStatus.DELIVERY')
        case _ : raise Exception(f'Incorrect status information with OpenStatus.{element.open_status}')
    return element.payment_date, element.delivery_date








