
import pyodbc
import requests
import json

DB_NAME = 'SBO_TDPC_PROD'


## string connection
def get_conn_sql(db_name=DB_NAME):
    """
        args:
            db_name: str database name
        return:
            pyodbc connection
    """
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=TDPSERVERW19;DATABASE=%s;UID=sa;PWD=Passw0rd' % db_name)
    return conn

URL_BASE = 'https://192.168.208.109:50000'

LOGIN_URL = f'{URL_BASE}/b1s/v1/Login'

def login(user_name, password, company_db):
    """
        args:
            user_name: str 
            password: str
            company_db: str
        return:
            str: session_id
    """

    credentials = {
        'CompanyDB': company_db,
        'UserName': user_name,
        'Password': password
    }
    headers = {
        'Content-Type': 'application/json'
    }
    json_data = json.dumps(credentials)
    # Realizar la solicitud POST para el inicio de sesión
    response = requests.post(LOGIN_URL, data=json_data, headers=headers, verify=False)

    # check 
    if response.status_code == 200:
        return response.json()['SessionId']
    else:
        raise Exception(response.json()['error']['message']['value'])


