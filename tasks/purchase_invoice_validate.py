import pandas as pd
import gspread as gs
from tasks.crear_factura_ER import * 
import gspread as gs
import warnings
import json
import requests
from .utils import URL_BASE
from .helpers import get_withholding_tax_codes, get_business_partner, put_business_partner
from rich.console import Console
import datetime
import calendar
from typing import TypedDict
import pandas as pd
from tqdm import tqdm

console = Console(record=True)
print = console.print

warnings.filterwarnings('ignore')

estadoCo = {
    '0': 'NO EXISTE',
    '1': 'ACEPTADO',
    '2': 'ANULADO',
    '3': 'AUTORIZADO',
    '4': 'NO AUTORIZADO',
}

estadoRuc = {
    '00': 'ACTIVO',
    '01': 'BAJA PROVISIONAL',
    '02': 'BAJA PROV. POR OFICIO',
    '03': 'SUSPENSION TEMPORAL',
    '10': 'BAJA DEFINITIVA',
    '11': 'BAJA DE OFICIO',
    '22': 'INHABILITADO-VENT.UNICA',
}

condDomiRuc = {
    '00': 'HABIDO',
    '09': 'PENDIENTE',
    '11': 'POR VERIFICAR',
    '12': 'NO HABIDO',
    '20': 'NO HALLADO',
}


columns = [
    'Numero SAP',
    'Proveedor',
    'Razon Social',
    'Fecha de Emision',
    'Tipo de Comprobante',
    'Serie',
    'Numero',
    'Monto',
    'Estado Comprobante',
    'Estado RUC',
    'Condicion Domicilio RUC',
    'Observaciones',
    'Mensaje'
]



def get_purchase_invoice_data(session_id: str, period: str):
    """Reads the purchase invoice data from SAP
    Args:
        date (str): date in format yyyy-mm
        session_id (str): session id of SAP
    """
    year = int(period.split('-')[0])
    month = int(period.split('-')[1])
    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime.date(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime.date(year, month, last_day).strftime('%Y-%m-%d')
    url = f"{URL_BASE}/b1s/v1/PurchaseInvoices?$filter=DocDate ge '{start_date}' and DocDate le '{end_date}'"
    docs = []
    
    def get_data(url: str):
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'B1SESSION={session_id}'
        }
        res = requests.get(url, headers=headers, verify=False)

        if res.status_code != 200:
            print(res.json())
        else:
            return res.json()
    
    while True:
        data = get_data(url)
        docs.extend(data['value'])
        if 'odata.nextLink' not in data:
            break
        url = f"{URL_BASE}/b1s/v1/{data['odata.nextLink']}"
        
    return docs

def login_sunat():
    client_id = '82fb43db-36b0-48b4-ae43-71be417a6f13'
    client_secret = 'v/kXAEoY4cH2m7qLJOX7sQ=='
    url = f"https://api-seguridad.sunat.gob.pe/v1/clientesextranet/{client_id}/oauth2/token/"
    
    params = {
        "grant_type": "client_credentials",
        "scope": "https://api.sunat.gob.pe/v1/contribuyente/contribuyentes",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    res = requests.post(url, data=params, headers=headers)
    res.json()
    ## if res.status_code != 200:
    ##     print("[bold red]Error al iniciar sesión en sunat[/]")
    ##     print(res.json())
        
    return res.json()['access_token']
    

class DataType(TypedDict):
    numRuc: str
    codComp: str
    numeroSerie: str
    numero: str
    fechaEmision: str
    monto: float
    
    
def validate_sunat(access_token: str, doc: dict):
    ruc = '20100286476'
    headers = {
        'Authorization': f'Bearer {access_token}',
        "Accept": "application/json"
    } 
    monto  =  doc['DocTotal'] + doc['WTAmount'] if doc['DocCurrency'] == 'S/' else doc['DocTotalFC'] + doc['WTAmountFC']
    data: DataType = {
        'numRuc': doc['CardCode'].replace('P', ''),
        'codComp': doc['U_SYP_MDTD'],
        'numeroSerie': doc['U_SYP_MDSD'],
        'numero': doc['U_SYP_MDCD'],
        'fechaEmision': datetime.datetime.strptime(doc['TaxDate'], '%Y-%m-%d').strftime('%d/%m/%Y'),
        'monto': monto,
    }
    
    url = f"https://api.sunat.gob.pe/v1/contribuyente/contribuyentes/{ruc}/validarcomprobante"
    
    res = requests.post(url, json=data, headers=headers)
    #if res.status_code != 200:
    #    print(res.json())
    #    print(data)
    
    row = [
        doc['DocNum'],
        doc['CardCode'],
        doc['CardName'],
        data['fechaEmision'],
        data['codComp'],
        data['numeroSerie'],
        data['numero'],
        data['monto'],
        estadoCo.get(res.json().get('data', {}).get('estadoCp', '')),
        estadoRuc.get(res.json().get('data', {}).get('estadoRuc', '')),
        condDomiRuc.get(res.json().get('data', {}).get('condDomiRuc', '')),
        res.json().get('data', {}).get('observaciones', ''),
        res.json().get('message', '')
    ]

    return pd.Series(row, index=columns)

    

WB = 'https://docs.google.com/spreadsheets/d/187YL6JYn4wBcjkR4bkbQCNlqjsGzzLqPhNcYF8W7X0A/edit#gid=0'

def write_to_excel(df: pd.DataFrame, perid: str):
    gc = gs.service_account(filename='tdpcorp-139fbe6dbc3c.json')
    workbook = gc.open_by_url(WB)
    # check if sheet exists
    if perid in [sheet.title for sheet in workbook.worksheets()]:
        # clear sheet
        worksheet = workbook.worksheet(perid)
        worksheet.clear()
    else:
        # create new sheet
        worksheet = workbook.add_worksheet(title=perid, rows=len(df), cols=len(columns))
    # write data
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    
        
def run(session_id: str, period: str):
    data = get_purchase_invoice_data(session_id, period)
    df = pd.DataFrame(columns=columns)
    pbar = tqdm(data)
    access_token = login_sunat()
    for doc in pbar:
        df.loc[len(df)] = validate_sunat(access_token, doc)
        pbar.set_description(f"Validando {doc['NumAtCard']}")
    print(df)
    write_to_excel(df, period)
    
    print(f'[bold green]Ver resultados en[/] {WB}')