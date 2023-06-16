from tasks import crear_factura_ER
from rich.console import Console
from tasks import crear_factura_proveedores
import pyfiglet
import click


console = Console(record=True)
print = console.print
    
if __name__ == '__main__':
    welcome = pyfiglet.figlet_format('TDP corp .')
    print(f'[bold red]{welcome}[/]')
    print('[bold red]Bienvenido a la automatización de procesos en SAP \n[/]')

    print('[bold]Ingresa tus credenciales[/]')
    user = click.prompt('Usuario', type=str)
    password = click.prompt('Contraseña', type=str, hide_input=True)
    
    session_id = ''
    while not session_id:
        try:
            session_id = crear_factura_proveedores.login(user, password)
        except Exception as e:
            print(e)
            user = click.prompt('Usuario', type=str)
            password = click.prompt('Contraseña', type=str, hide_input=True)
        else:
            print('[bold green]Ha iniciado sesión correctamente[/] \n')

    crear_factura_proveedores.run(session_id)

    
    
