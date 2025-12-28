
def find_open_date(dict_:dict):
    for key, value in dict_.items():
        if 'close' in value:
            continue
        return value['date']

def status_date_refactor(rows, name):
    for row in rows:
        if name in row:
            row['status_date']=find_open_date(row[name]) if row.get(name) is not None else None
    return rows

