from tasks import purchase_invoice, purchase_invoice_validate
from rich.console import Console
import inquirer

console = Console(record=True)
print = console.print

VALIDAR_DOCS ='Validar documentos en sunat'
EE_RR = 'Cargar entregas a rendir'

def select_task() -> str:
    """Selects a task from the list of tasks."""
    
    tasks = [
        VALIDAR_DOCS,
        EE_RR
    ]
    
    options = [
        inquirer.List('task', 
                      message='Selecciona la tarea a realizar', 
                      choices=tasks,
                      carousel=True)
    ]
    
    anwasers = inquirer.prompt(options)
    task = anwasers['task']
    print(f'[bold]Seleccionaste la tarea {task}[/] \n')
    return task
    
    
def run_task(task: str, session_id: str):
    """Runs the task selected by the user."""
    print(task, VALIDAR_DOCS)
    if task == VALIDAR_DOCS:
        while True:
            piriod = input('Ingrese el periodo en formato yyyy-mm: ')
            # validar formato yyyy-mm
            if len(piriod) == 7 and piriod[4] == '-':
                break
            
        purchase_invoice_validate.run(session_id, piriod)
    elif task == EE_RR:
        purchase_invoice.run(session_id)
    else:
        raise ValueError(f'Invalid task {task}')