import requests
from .utils import get_conn_sql, URL_BASE, login
from rich.console import Console


console = Console(record=True)
print = console.print

def get_withholding_tax_codes(code, session_id):
    """
        args:
            code: str
            session_id: str
        return:
            dict with withholding tax code
    """
    url = f"{URL_BASE}/b1s/v1/WithholdingTaxCodes('{code}')"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'[red]withholding tax code {code} not found[/red]')
        raise Exception(response.json())
    

def get_business_partner(card_code, session_id):
    """
        args:
            card_code: str
            session_id: str
        return:
            dict with business partner
    """
    url = f"{URL_BASE}/b1s/v1/BusinessPartners('{card_code}')"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'[red]business partner {card_code} not found[/red]')
        raise Exception(response.json())
