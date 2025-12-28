class Supplier:

    def __init__(self, supplier):
       self.supplier_id = supplier['supplier_id']
       self.name = supplier['name']
       self.contracts = []
       self.accounts = []

    def add_contract(self, contract):
        self.contracts.append(contract)

    def add_account(self, account):
        self.accounts.append(account)


class Contract:

    def __init__(self, contract):
        self.contract_id = contract['contract_id']
        self.contract = contract['contract']
        self.contract_type = contract['type']
        self.lifetime = contract['lifetime']
        self.accounts = []
        self.specifications = []

    def add_account(self, account):
        self.accounts.append(account)

    def add_specification(self, specification):
        self.specifications.append(specification)

class Account:

    def __init__(self,  account):
        self.account = account['account']
        self.account_id = account['account_id']
        self.open_status = account['open_status']
        self.status_date = account['status_date']
        self.employee_name = account['first_name']
        self.description = account['description']

class Specification:

    def __init__(self, specification):
        self.specification = specification['specification']
        self.specification_id = specification['specification_id']
        self.open_status = specification['open_status']
        self.status_date = specification['status_date']
        self.employee_name = specification['first_name']
        self.description = specification['description']
