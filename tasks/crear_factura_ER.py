from rich.console import Console
from RPA.Desktop import Desktop
from RPA.Windows import Windows
from time import sleep
import gspread as gs

console = Console(record=True)
print = console.print


win = Windows()
desk = Desktop()

gc = gs.service_account(filename='tdpcorp-139fbe6dbc3c.json')
WB = 'https://docs.google.com/spreadsheets/d/11HyZN62kfRManwuUz5jNDj7wtr8YFWJz1M5zWlTcS9Q/edit#gid=0'
workbook = gc.open_by_url(WB)
    

def leer_hoja():
    worksheet = workbook.get_worksheet_by_id(0)
    data = worksheet.row_values(2)
    return data


def escribir_hoja(data, is_success: bool):
    sheet_id =  832139710 if is_success else 1757171547
    worksheet = workbook.get_worksheet_by_id(sheet_id)
    worksheet.insert_row(data, 2)
    # delete
    worksheet = workbook.get_worksheet_by_id(0)
    worksheet.delete_row(2)
    

def formulario_factura_de_proveedores():
    win.control_window('Formulario de búsqueda principal')
    win.send_keys(keys='{Ctrl}{F3}')
    win.send_keys(keys='Factura de proveedores', send_enter=True)
    print('Formulario de factura de proveedores abierto')
    sleep(1)


def llenar_datos_factura(data):
    proveedor, fecha_doc, fecha_cont, serie, correlativo, centro_costo, \
            unidad_negocio, local, canal_distr, \
            servicio, precio, comentarios, n_ccer = data
    win.send_keys(keys=proveedor)
    win.send_keys(keys='{TAB}'*7)
    win.send_keys(keys=fecha_cont.strip())
    win.send_keys(keys='{TAB}'*2)
    win.send_keys(keys=fecha_doc.strip())
    win.send_keys(keys='{TAB}')
    sleep(0.5)
    win.send_keys(keys='{DOWN}'*2)
    sleep(0.5)
    win.send_keys(keys='{ENTER}')
    sleep(0.5)
    win.send_keys(keys='{CTRL}H')
    win.send_keys(keys='{SHIFT}{TAB}')
    win.send_keys(keys=servicio.strip())
    win.send_keys(keys='{TAB}'*3)
    win.send_keys(keys=centro_costo.strip())
    sleep(0.5)
    win.send_keys(keys='{TAB}')
    win.send_keys(keys=unidad_negocio.strip())
    sleep(0.5)
    win.send_keys(keys='{TAB}')
    win.send_keys(keys=local)
    sleep(0.5)
    win.send_keys(keys='{TAB}')
    win.send_keys(keys=canal_distr.strip())
    sleep(0.5)
    win.send_keys(keys='{TAB}')
    win.send_keys(keys=precio)
    sleep(0.5)
    win.send_keys(keys='{CTRL}R')
    win.send_keys(keys=f'{comentarios.strip()} Creado por: robot')

    control = win.control_window('name:"Campos: Parametriz..." and and type:Window')
    desk.click(f'coordinates:{control.right - 50},{control.top + 42}')
    win.send_keys(keys='01')
    win.send_keys(keys='{TAB}')
    sleep(0.5)
    win.send_keys(keys=serie.strip())
    win.send_keys(keys='{TAB}')
    sleep(0.5)
    win.send_keys(keys=correlativo.strip())
    win.send_keys(keys='{TAB}'*2)
    win.send_keys(keys='{DOWN}'*8, send_enter=True)
    # add Numero CC/ER
    win.send_keys(keys='{TAB}')
    win.send_keys(keys=n_ccer.strip())


def crear_factura():
    control = win.control_window('name:"Factura de proveedores" and type:Window')
    # check scroll
    desk.click(f'coordinates:{control.right - 20},{control.bottom - 25}')
    sleep(1)
    desk.click(f'coordinates:{control.left + 90},{control.bottom - 25}')
    win.send_keys(keys='{DOWN}'*2)
    sleep(1)
    win.send_keys(keys='{ENTER}')
    sleep(1)
    win.send_keys(keys='{ENTER}')


def job():
    data = leer_hoja()
    if not data:
        sleep(5)
        win.close_current_window()
        return
    try:
        formulario_factura_de_proveedores()
        llenar_datos_factura(data)
        crear_factura()
    except Exception as e:
        print(e)
        escribir_hoja(data, False)
        print(f'[bold red]Error al crear la factura 01-{data[2]}-{data[3]} [/bold red]')
    else:
        escribir_hoja(data, True)
        print(f'[bold green]Factura creada con éxito 01-{data[2]}-{data[3]} [/bold green]')
    job()
    
          
