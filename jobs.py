from tasks import crear_factura_ER
from rich.console import Console
from tasks import purchase_invoice
import pyfiglet
import click
import inquirer


console = Console(record=True)
print = console.print
    
if __name__ == '__main__':
    welcome = pyfiglet.figlet_format('TDP corp .')
    print(f'[bold red]{welcome}[/]')
    print('[bold red]Bienvenido a la automatización de procesos en SAP \n[/]')

    
    companies = [
        {'name': 'TDP CORP S.A.', 'value': 'SBO_TDPC_PROD'},
        {'name': 'TEST', 'value': 'SBO_TDPC_TEST'},
    ]

    options = [
        inquirer.List('company', 
                      message='Selecciona la compañia', 
                      choices=[company['name'] for company in companies],
                      carousel=True)
    ]
    answers = inquirer.prompt(options)
    company_db = next(company['value'] 
                      for company in companies 
                      if company['name'] == answers['company'])
    print(f'[bold]Seleccionaste la compañia {company_db}[/] \n')

    print('[bold]Ingresa tus credenciales[/]')
    user = click.prompt('Usuario', type=str)
    password = click.prompt('Contraseña', type=str, hide_input=True)


    
    session_id = ''
    while not session_id:
        try:
            session_id = purchase_invoice.login(user, password, company_db)
        except Exception as e:
            print(e)
            user = click.prompt('Usuario', type=str)
            password = click.prompt('Contraseña', type=str, hide_input=True)
        else:
            print('[bold green]Ha iniciado sesión correctamente[/] \n')

    purchase_invoice.run(session_id)

    
    
