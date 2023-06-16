import pandas as pd
import gspread as gs
from tasks.crear_factura_ER import * 
import gspread as gs
import warnings
import json
import requests
from .utils import get_conn_sql, URL_BASE, login
from rich import print

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

gc = gs.service_account(filename='tdpcorp-139fbe6dbc3c.json')
WB = 'https://docs.google.com/spreadsheets/d/11HyZN62kfRManwuUz5jNDj7wtr8YFWJz1M5zWlTcS9Q/edit#gid=0'
workbook = gc.open_by_url(WB)
worksheet = workbook.get_worksheet_by_id(0)


def read_data():
    """
    return: 
        DataFrame
    """
    # cargar en un dataframe
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    # completar datos en tipo blanco y na
    df['Tipo de Documento'] = df['Tipo de Documento'].replace('', '01').fillna('01')

    # actualizar tipo de compra solo si Numero CC/ER esta vacio
    df.loc[df['Numero CC/ER'] == '', 'Tipo de Compra'] = '01'
    df['Tipo de Compra'] = df['Tipo de Compra'].fillna('CC')

    # casting to datetime format dd.mm.yyyy
    df['Fecha de contabilización'] = pd.to_datetime(df['Fecha de contabilización'], format='%d.%m.%Y')
    df['Fecha del documento'] = pd.to_datetime(df['Fecha del documento'], format='%d.%m.%Y')
    df['Fecha de vencimiento'] = pd.to_datetime(df['Fecha de vencimiento'], format='%d.%m.%Y')
    # casting to float
    df['Precio por unidad'] = df['Precio por unidad'].astype(float)
    df['Total (ML)'] = df['Total (ML)'].astype(float)
    # add services name
    servicios_df = ger_services(conn, df['Codigo de Gasto'].unique())[['Code', 'U_SYP_Concepto']]
    df = df.merge(servicios_df, left_on='Codigo de Gasto', right_on='Code', how='left')
    # add index
    df['No.Ref.del acreedor'] = df['Tipo de Documento'].str.cat(df[['Serie del Documento','Correlativo del Documento']], sep='-')
    df.set_index('No.Ref.del acreedor', inplace=True)
    return df


def make_invoices(df):
    invoices = []
    new_df = df[df['DocNum'] == '']
    for index in new_df.index.unique():
        infoice_df = df.loc[[index]]
        invoice = {
            "CardCode": infoice_df['Proveedor'].iloc[0],
            "NumAtCard": index,
            # fechas
            "DocDate": infoice_df['Fecha de contabilización'].iloc[0].strftime('%Y-%m-%d'),
            "DocDueDate": infoice_df['Fecha de vencimiento'].iloc[0].strftime('%Y-%m-%d'),
            "TaxDate": infoice_df['Fecha del documento'].iloc[0].strftime('%Y-%m-%d'),
            "DocType": "S",
            # Numero de factura
            "U_SYP_MDTD": infoice_df['Tipo de Documento'].iloc[0],
            "U_SYP_MDSD": infoice_df['Serie del Documento'].iloc[0],
            "U_SYP_MDCD": infoice_df['Correlativo del Documento'].iloc[0],
            "U_SYP_TCOMPRA": infoice_df['Tipo de Compra'].iloc[0],
            "comments": infoice_df['Comentarios'].iloc[0],
        }
        if infoice_df['Tipo de Compra'].iloc[0] == 'CC':
            invoice['U_SYP_CODERCC'] = infoice_df['Numero CC/ER'].iloc[0]

        invoice_lines = []
        for index, row in infoice_df.iterrows():
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
                "LineTotal": row['Total (ML)']
            })

        invoice['DocumentLines'] = invoice_lines
        invoices.append(invoice)
    return invoices


def create_invoice(invoice, session_id):
    """
        args:
            invoice: dict
            session_id: str
        return:
            dict
    """
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }
    json_data = json.dumps(invoice)
    response = requests.post(f'{URL_BASE}/b1s/v1/PurchaseInvoices', data=json_data, headers=headers, verify=False)
    return response.json()


def run(session_id):
    df = read_data()
    invoices = make_invoices(df)
    # documentos creados
    df['Processed'] = False
    for invoice in invoices:
        req = create_invoice(invoice, session_id)
        df.loc[invoice["NumAtCard"], "Processed"] = True
        try:
            df.loc[req["NumAtCard"], "DocNum"] = str(req["DocNum"])
        except:
            df.loc[invoice["NumAtCard"], "Error"] = req["error"]["message"]["value"]
    print(df[df["Processed"]][['DocNum', 'Error']].fillna('-'))

    # update google sheet
    doc_num = df['DocNum'].fillna('').to_numpy().reshape(-1, 1)
    worksheet.update('W2', doc_num.tolist())
    errors = df['Error'].fillna('').to_numpy().reshape(-1, 1)
    worksheet.update('X2', errors.tolist())