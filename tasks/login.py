from RPA.core.windows.context import WindowControlError
from rich.console import Console
from RPA.Windows import Windows
from time import sleep
import click

console = Console(record=True)
print = console.print

win = Windows()


def verificar_BPS():
    print('BPS Verificando...')
    sleep(5)
    try:
        win.control_window('name:"Mensaje sistema" and type:Window', timeout=1)
    except WindowControlError as e:
        verificar_BPS()
    else:
        print('[bold green]BPS verificado[/] \n')
        win.send_keys(keys='{ENTER}')


def login_sap():
    print('[bold]Ingresa tus credenciales[/]')
    user = click.prompt('Usuario', type=str)
    password = click.prompt('Contraseña', type=str, hide_input=True)
    
    click.confirm('\n No puedes usar la maquina mientras se ejecuta el '\
                  'proceso, ¿Deseas continuar? \n', abort=False)
    
    click.option('--user', prompt='Usuario', help='Usuario SAP')
    
    win.windows_search('SAP Business One')
    try:
        win.control_window('SAP Business One')
    except Exception as e:
        win.send_keys(keys='{ENTER}')
        
    win.control_window('SAP Business One')
    win.send_keys(keys=f' {user}')
    win.send_keys(keys='{TAB}')
    win.send_keys(keys=f' {password}', send_enter=True)
    try:
        win.control_window('Seleccionar sociedad')
    except WindowControlError:
        print('[bold green]Credenciales correctas[/] \n')
        sleep(10)
        verificar_BPS()
    else:
        print('[bold red]Las credenciales no son correctas, intenta de nuevo[/] \n')
        win.close_window('Seleccionar sociedad')
        login_sap()
        

#if __name__ == '__main__':
#    login_sap()