import requests
from .utils import get_conn_sql, URL_BASE, login
from rich.console import Console
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
import re

console = Console(record=True)
print = console.print

def get_withholding_tax_codes(session_id: str, code: str):
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
    

def get_business_partner(session_id: str, card_code: str):
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


def create_business_partner(session_id: str, code: str):
    """
    """
    url = f"{URL_BASE}/b1s/v1/BusinessPartners"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }
    chromedriver_autoinstaller.install() 
    driver = webdriver.Chrome()
    url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias'
    driver.get(url)
    # get only numbers 
    ruc = re.sub("[^0-9]", "", code)
    driver.find_element(By.ID, 'txtRuc').clear()
    driver.find_element(By.ID, 'txtRuc').send_keys(ruc)
    driver.find_element(By.ID, 'btnAceptar').click()
    
    razonsocial = driver.find_elements(By.CSS_SELECTOR, '.list-group-item-heading:last-child')[1].text.split('-')[1].strip()
    activo = driver.find_element(By.XPATH, "//*[contains(text(), 'Estado del Contribuyente:')]").find_element(By.XPATH, '../..').text.split(':')[1].strip()
    if activo != 'ACTIVO':
        raise Exception(f'business partner {code} not active')
    
    
    


def put_business_partner(session_id: str, code: str, data: dict):
    """
        args:
            card_code: str
            session_id: str
            data: dict
        return:
            dict with business partner
    """
    url = f"{URL_BASE}/b1s/v1/BusinessPartners('{code}')"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'B1SESSION={session_id}'
    }
    response = requests.patch(url, json=data, headers=headers, verify=False)
    if response.status_code == 204:
        return data
    else:
        print(f'[red]business partner {code} not found[/red]')
        raise Exception(response.json())
