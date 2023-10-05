import pandas as pd
import gspread as gs
from tasks.crear_factura_ER import * 
import gspread as gs
import warnings
import json
import requests
from .utils import get_conn_sql, URL_BASE, login
from .helpers import get_withholding_tax_codes, get_business_partner, put_business_partner
from msal import PublicClientApplication
from rich.console import Console

console = Console(record=True)
print = console.print

warnings.filterwarnings('ignore')


def ger_services(conn, codes):
    """
        args:
            conn: pyodbc connection
            codes: list of codes
        return:
            DataFrame
    """

    query = """SELECT *
     FROM [@SYP_SERVICIOS] T0 WHERE T0.[Code] IN (%s)""" % ','.join([str(f"'{c}'") for c in codes])
    df = pd.read_sql(query, conn)
    return df


conn = get_conn_sql()

#gc = gs.service_account(filename='tdpcorp-139fbe6dbc3c.json')
#WB = 'https://docs.google.com/spreadsheets/d/11HyZN62kfRManwuUz5jNDj7wtr8YFWJz1M5zWlTcS9Q/edit#gid=0'
#workbook = gc.open_by_url(WB)
#worksheet = workbook.get_worksheet_by_id(0)
client_id = "c86e6215-9b41-4dd7-a33e-1f2eb9a9bbe7"
tenant_id = "8d1ddc2f-b8f7-4ce4-abc1-020b322d8288"

app = PublicClientApplication(
    client_id=client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)
url =  'https://graph.microsoft.com/v1.0/me/drive/root:/robots/Entregas a rendir.xlsx'

def ms_365_login():
    result = None
    accounts = app.get_accounts()
    if accounts:
        # If so, you could then somehow display these accounts and let end user choose
        print("Pick the account you want to use to proceed:")
        for a in accounts:
            print(a["username"])
        # Assuming the end user chose this one
        chosen = accounts[0]
        # Now let's try to find a token in cache for this account
        result = app.acquire_token_silent(["User.Read", 'files.readwrite.all'], account=chosen)
    
    if not result:
        # So no suitable token exists in cache. Let's get a new one from Azure AD.
        result = app.acquire_token_interactive(scopes=["User.Read", 'files.readwrite.all'])
    if "access_token" in result:
        print("Has iniciado sesión en Microsoft 365")
        claims = result.get("id_token_claims")
        print(f"Cuenta 365: {claims['name']} <{claims['preferred_username']}>")
        return result["access_token"]
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))
        raise Exception('Error al iniciar sesión en Microsoft 365')
    
def write_data(df):
    access_token = ms_365_login()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    worksheet_name = 'Hoja1'
    
    doc_num = df['DocNum'].fillna('').to_numpy().reshape(-1, 1)
    errors = df['Error'].fillna('').to_numpy().reshape(-1, 1)
    
    request_body = {
        "values": errors.tolist(),
    }
    target_cell_range = f"Z2:Z{len(errors) + 1}"
    target_cell_range_url = f'{url}:/workbook/worksheets(\'{worksheet_name}\')/range(address=\'{target_cell_range}\')'
    res = requests.patch(target_cell_range_url, json=request_body, headers=headers)
    if res.status_code != 200:
        print (res.json())
        print ('Error al actualizar el archivo de microsoft 365')
    
    
    
    errors = df['Error'].fillna('').to_numpy().reshape(-1, 1)

def read_data():
    """
    return: 
        DataFrame
    """
    # cargar en un dataframe
    #data = worksheet.get_all_values()
    access_token = ms_365_login()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    res = requests.get(f'{url}:/content', headers=headers)
    if res.status_code != 200:
        print (res.json())
        raise Exception('Error al leer el archivo de microsoft 365')
    
    df = pd.read_excel(res.content, dtype={
        'Proveedor': str,
        'Fecha de contabilización': str,
        'Fecha de vencimiento': str,
        'Fecha del documento': str,
        'Tipo de Documento': str,
        'Serie del Documento': str,
        'Correlativo del Documento': str,
        'Numero CC/ER': str,
        'Tipo Operación - DET': str,
        'Código DET': str,
        'Auto-Detracción': str,
        'Comentarios': str,
        'Total del documento': float,
        'Codigo de Gasto': str,
        'Centro de Costos': str,
        'Unidad de negocio': str,
        'Local	Canal de distribución': str ,
        'Precio por unidad': float,
        'Indicador de impuestos': str,
        'Sujeto a retención': str,
        'Total (ML)': float,
        'Moneda': str,
        'DocNum': str,
        'Error': str,
    }, usecols='A:Y')
    # completar datos en tipo blanco y na
    df['Tipo de Documento'] = df['Tipo de Documento'].replace('', '01').fillna('01').str.zfill(2)

    # actualizar tipo de compra solo si Numero CC/ER esta vacio
    df.loc[df['Numero CC/ER'] == '', 'Tipo de Compra'] = '01'
    df['Tipo de Compra'] = df['Tipo de Compra'].fillna('CC')

    # casting to datetime format dd.mm.yyyy
    df['Fecha de contabilización'] = pd.to_datetime(df['Fecha de contabilización'], format='%d.%m.%Y')
    df['Fecha del documento'] = pd.to_datetime(df['Fecha del documento'], format='%d.%m.%Y')
    df['Fecha de vencimiento'] = pd.to_datetime(df['Fecha de vencimiento'], format='%d.%m.%Y')
    # remove spaces and commas as to float
    df['Precio por unidad'] = df['Precio por unidad'].astype(float)
    df['Total (ML)'] = df['Total (ML)'].astype(float)
    df['Total del documento'] = df['Total del documento'].astype(float)

    # add services name
    servicios_df = ger_services(conn, df['Codigo de Gasto'].unique())[['Code', 'U_SYP_Concepto']]
    df = df.merge(servicios_df, left_on='Codigo de Gasto', right_on='Code', how='left')
    # add index
    df['No.Ref.del acreedor'] = df['Tipo de Documento'].str.cat(df[['Serie del Documento','Correlativo del Documento']], sep='-')
    df.set_index('No.Ref.del acreedor', inplace=True)

    # remove withspaces
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[~(df.Proveedor.isna()) & ~(df.Proveedor == '')]
    return df


def make_invoices(df, session_id):
    invoices = []
    new_df = df[(df['DocNum'] == '') | (df['DocNum'] == "\xa0") | (df['DocNum'].isna())]
    for index in new_df.index.unique():
        invoice_df = df.loc[[index]]
        invoice = {
            "CardCode": invoice_df['Proveedor'].iloc[0],
            "NumAtCard": index,
            # fechas
            "DocDate": invoice_df['Fecha de contabilización'].iloc[0].strftime('%Y-%m-%d'),
            "DocDueDate": invoice_df['Fecha de vencimiento'].iloc[0].strftime('%Y-%m-%d'),
            "TaxDate": invoice_df['Fecha del documento'].iloc[0].strftime('%Y-%m-%d'),
            "DocType": "S",
            # Numero de factura
            "U_SYP_MDTD": invoice_df['Tipo de Documento'].iloc[0],
            "U_SYP_MDSD": invoice_df['Serie del Documento'].iloc[0],
            "U_SYP_MDCD": invoice_df['Correlativo del Documento'].iloc[0],
            "U_SYP_TCOMPRA": invoice_df['Tipo de Compra'].iloc[0],
            "Comments": f"""
                {invoice_df['Comentarios'].iloc[0]} \n creado por bot
            """,
            "JournalMemo": invoice_df['Comentarios'].iloc[0],
        }

        business_partner = get_business_partner(session_id, invoice_df['Proveedor'].iloc[0])

        if invoice_df['Auto-Detracción'].iloc[0]:
            invoice['U_SYP_AUDET'] = invoice_df['Auto-Detracción'].iloc[0]
            invoice['U_SYP_TPO_OP'] = '01'

        if invoice_df['Tipo de Compra'].iloc[0] == 'CC':
            invoice['U_SYP_CODERCC'] = invoice_df['Numero CC/ER'].iloc[0]

        if invoice_df['Tipo Operación - DET'].iloc[0]:
            invoice['U_SYP_TPO_OP'] = invoice_df['Tipo Operación - DET'].iloc[0]

        # Código DET
        if invoice_df['Código DET'].iloc[0]:
            code = invoice_df['Código DET'].iloc[0]
            try:
                data = get_withholding_tax_codes(session_id, code)
            except:
                raise Exception(f'Código DET {invoice_df["Código DET"].iloc[0]} no es valido')
            rate = data['Rate']
            total = invoice_df['Total (ML)'].sum()
            try:
                amount = round(total * rate / 100, 0)
            except Exception as e:
                print(e)
                raise Exception(f'Verifique el monto del documento {index}')

            invoice['WithholdingTaxDataCollection'] = [{
                "WTCode": code,
                "WTAmount": amount,
            }]
        else:
            code = business_partner['WTCode']
            if code:
                invoice['WithholdingTaxDataCollection'] = [{
                "WTCode": code,
                "WTAmount": 0.,
            }]
                
        # currency add curSource and docCur
        if invoice_df['Moneda'].iloc[0]:
            invoice['DocCurrency'] = invoice_df['Moneda'].iloc[0]
            invoice['CurrencySource'] = 'C'

        invoice_lines = []
        for index, row in invoice_df.iterrows():
            invoice_lines.append({
                "AccountCode": row['Codigo de Gasto'],
                "U_SYP_TIPOSERV": row['Codigo de Gasto'],
                # descripcion
                "ItemDescription": row['U_SYP_Concepto'],
                "Quantity": 1,
                "UnitPrice": row['Precio por unidad'],
                "TaxCode": row['Indicador de impuestos'],
                # centro de costo
                "CostingCode": row['Centro de Costos'],
                "CostingCode2": row['Unidad de negocio'],
                "CostingCode3": row['Local'],
                "CostingCode4": row['Canal de distribución'],
                # Total (ML)
            })

        invoice['DocumentLines'] = invoice_lines
        invoices.append(invoice)
    return invoices


def invoice_exists(session_id: str, num_at_card: str):
    """
    """
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }
    url = f"{URL_BASE}/b1s/v1/PurchaseInvoices?$filter=NumAtCard eq '{num_at_card}'"
    
    response = requests.get(url, headers=headers, verify=False)
    
    
    data = response.json()
    
    # check error
    if 'error' in data:
        raise Exception(data['error']['message']['value'])
    # check if exists
    if data['value']:
        raise Exception(f'the invoice {num_at_card} already exists, N° SAP {data["value"][0]["DocNum"]}')
    
def create_invoice(invoice, session_id):
    """
        args:
            invoice: dict
            session_id: str
        return:
            dict
    """
    
    # check if exists
    invoice_exists(session_id, invoice['NumAtCard'])
    
    
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }

    # check currency type

    if invoice['DocCurrency'] == 'S/' and invoice['CardCode'] != '4011111':
        put_business_partner(session_id, invoice['CardCode'], {
            "DebitorAccount": "4211111"
        })
    elif invoice['DocCurrency'] == 'US$' and invoice['CardCode'] != '4011112':
        put_business_partner(session_id, invoice['CardCode'], {
            "DebitorAccount": "4211112"
        })

    json_data = json.dumps(invoice)
    url = f'{URL_BASE}/b1s/v1/PurchaseInvoices'
    response = requests.post(url, data=json_data, headers=headers, verify=False)
    return response.json()


def run(session_id):
    df = read_data()
    try:
        invoices = make_invoices(df, session_id)
    except Exception as e:
        console.print_exception()
        return
    # documentos creados
    df['Processed'] = False
    for invoice in invoices:
        try:
            req = create_invoice(invoice, session_id)
            df.loc[req["NumAtCard"], "DocNum"] = str(req["DocNum"])
        except KeyError:
            df.loc[invoice["NumAtCard"], "Error"] = req["error"]["message"]["value"]
        except Exception as e:
            df.loc[invoice["NumAtCard"], "Error"] = str(e)
        else:
            df.loc[invoice["NumAtCard"], "Error"] = ''
        finally:
            df.loc[invoice["NumAtCard"], "Processed"] = True

    write_data(df)
    df_processed = df[df["Processed"]][['DocNum', 'Error']].fillna('-')
    print(df_processed)
    