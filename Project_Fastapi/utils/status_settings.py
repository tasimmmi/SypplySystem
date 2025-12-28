from core.models import *

def check_account_status(element : Accounts | Contracts | Specifications):
    match element.payment_type:
        case PaymentTypeEnum.PREPAYMENT_100:
            for key, value in element.payment_date.items():
                if 'date' not in value:
                    raise Exception('Missing required keys: date or close')
                elif 'close' not in value:
                    return OpenStatusEnum.PAYMENT
            for key, value in element.delivery_date.items():
                if 'close' in value:
                    return OpenStatusEnum.CLOSE
                elif 'date' in value or 'period' in value:
                    return OpenStatusEnum.DELIVERY
                else: raise Exception('Missing required keys: date')
        case PaymentTypeEnum.POSTPAYMENT_100:
            for key, value in element.delivery_date.items():
                if 'date' not in value:
                    raise Exception('Missing required keys: date')
                elif 'close' not in value:
                    return OpenStatusEnum.DELIVERY
            for key, value in element.payment_date.items():
                if 'close' in value:
                    print('work close')
                    return OpenStatusEnum.CLOSE
                elif 'date' in value or 'period' in value:
                    print('work')
                    return OpenStatusEnum.PAYMENT
            print('dont work')
            raise Exception('Incorrect status processing')
        case PaymentTypeEnum.PARTIAL_PRE_BEFORE:
            if [element.payment_date['1'], element.payment_date['2'], element.delivery_date['1']] is not None:
                if 'date' not in element.payment_date['1']:
                    raise Exception('Missing required keys: date or close')
                if 'close' not in element.payment_date['1'] or 'close' not in element.payment_date['2']:
                    return OpenStatusEnum.PAYMENT
                if 'close' not in element.delivery_date['1']:
                    return OpenStatusEnum.DELIVERY
                if 'close' in element.delivery_date['1']:
                    return OpenStatusEnum.CLOSE
                raise Exception('Incorrect status processing')
            raise Exception('Missing required payments and delivery dates')
        case PaymentTypeEnum.PARTIAL_PRE_AFTER:
            if [element.payment_date['1'], element.payment_date['2'], element.delivery_date['1']] is not None:
                if 'date' not in element.payment_date['1']:
                    raise Exception('Missing required keys: date or close')
                if 'close' not in element.payment_date['1']:
                    return OpenStatusEnum.PAYMENT
                if 'close' not in element.delivery_date['1']:
                    return OpenStatusEnum.DELIVERY
                if 'close' not in element.payment_date['2']:
                    return OpenStatusEnum.PAYMENT
                if 'close' in element.payment_date['2']:
                    return OpenStatusEnum.CLOSE
                raise Exception('Incorrect status processing')
            raise Exception('Missing required payments and delivery dates')

