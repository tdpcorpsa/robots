from tasks import crear_factura_ER
from rich.console import Console
from tasks import login
import pyfiglet


console = Console(record=True)
print = console.print
    
if __name__ == '__main__':
    welcome = pyfiglet.figlet_format('TDP corp .')
    print(f'[bold red]{welcome}[/]')
    print('[bold red]Bienvenido a la automatización de procesos en SAP \n[/]')
    
    login.login_sap()
    crear_factura_ER.job()
    
