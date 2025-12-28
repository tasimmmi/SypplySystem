from datetime import datetime


def report_refactor(_dict : list[dict]):
    overdue_message = []
    actual_message = []
    today_message = []
    print(_dict)
    for row in _dict:
        message = []
        if 'type' in row and row['type'] is not None:
            message.append(f"<b>{row['type']}</b>")
        if 'document' in row and row['document'] is not None:
            message.append( f" / {row['document']}")
        if 'parent' in row and row['parent'] is not None:
            message.append(f" -> {row['parent']}")
        if 'supplier_name' in row and row['supplier_name'] is not None:
            message.append(f" / {row['supplier_name']}")
        if 'payment_date' in row and row['payment_date'] is not None:
            for key, value in row['payment_date'].items():
                if 'date' in value and 'close' not in value:
                    message.append(f" / {value['name']}: {value['date']}")
                    if 'first_name' in row and row['first_name'] is not None:
                        message.append(f" / {row['first_name']}")
                    date = datetime.strptime(value['date'], '%Y-%m-%d').date()
                    if date > datetime.today().date():
                        actual_message.append(' '.join(message))
                    if date < datetime.today().date():
                        overdue_message.append(' '.join(message))
                    if date == datetime.today().date():
                        today_message.append(' '.join(message))
        if 'delivery_date' in row and row['delivery_date'] is not None:
            for key, value in row['delivery_date'].items():
                if 'date' in value and 'close' not in value:
                    message.append(f" / {value['name']}: {value['date']}")
                    if 'first_name' in row and row['first_name'] is not None:
                        message.append(f" / {row['first_name']}")
                    date = datetime.strptime(value['date'], '%Y-%m-%d').date()
                    if date > datetime.today().date():
                        actual_message.append(' '.join(message))
                    if date < datetime.today().date():
                        overdue_message.append(' '.join(message))
                    if date == datetime.today().date():
                        today_message.append(' '.join(message))


    overdue_line = "🟥 ПРОСТРОЧЕННЫЕ:\n" + '\n------\n'.join(overdue_message) if len(overdue_message)>0 else None

    actual_line = ('🟧 СРОК ИСТЕКАЕТ СЕГОДНЯ:\n'+ '\n------\n'.join(actual_message)) if len(actual_message)>0 else None
    today_line =('🟩 СРОК ИСТЕКАЕТ В ТЕЧЕНИИ 5 ДНЕЙ: \n'+ '\n------\n'.join(today_message)) if len(today_message)>0 else None

    return overdue_line, actual_line, today_line