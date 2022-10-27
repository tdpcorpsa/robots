from RPA.Windows import Windows
from time import sleep
import pprint

library = Windows()

USER = ' manager'
PASSWORD = ' 1234'


def verificar_BPS():
    print('BPS Verificando...')
    sleep(5)
    try:
        library.control_window('name:"Mensaje sistema" and type:Window', timeout=1)
    except Exception as e:
        verificar_BPS()
    else:
        print('BPS verificado')
        library.send_keys(keys='{ENTER}')


def login_sap():
    library.windows_search('SAP Business One')
    library.control_window('SAP Business One')
    library.send_keys(keys=USER)
    library.send_keys(keys='{TAB}')
    library.send_keys(keys=PASSWORD, send_enter=True)
    print('Autentificación exitosa')
    verificar_BPS()

#if __name__ == '__main__':
#    login_sap()

