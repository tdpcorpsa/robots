from login import login_sap
from RPA.Windows import Windows
from time import sleep
from datetime import datetime
from RPA.Desktop import Desktop


win = Windows()
desk = Desktop()


def formulario_de_entregas():
    win.control_window('Formulario de búsqueda principal')
    win.send_keys(keys='{Ctrl}{F3}')
    win.send_keys(keys='Entrega')
    win.send_keys(keys='{TAB}{TAB}{TAB}', send_enter=True)
    print('Formulario de entrega abierto')
    sleep(1)

    
def activar_busqueda():
    win.control_window('Entrega')
    win.control_window('name:"Datos" and type:ToolBar > name:"" and type:Button')
    win.send_keys(keys='{ENTER}')
    try:
        win.control_window('name:"Mensaje sistema" and type:Window', timeout=1)
    except:
        win.send_keys(keys='{ENTER}')
    else:
        win.send_keys(keys='{ENTER}{ENTER}')
    print('Formato de busca activada')
    sleep(1)

    
def parametros_busqueda():
    win.send_keys(keys='{TAB}{DOWN}')
    sleep(0.5)
    win.send_keys(keys='{DOWN}{ENTER}')
    sleep(0.2)
    win.send_keys(keys='{TAB}')
    sleep(0.2)
    fecha = datetime.now().strftime('%d/%m/%Y')
    win.send_keys(keys=fecha)
    sleep(0.1)
    win.send_keys(keys='{DOWN}')
    sleep(0.1)
    win.send_keys(keys='{ENTER}')
    print('Parametros de busqueda establecidos')
    sleep(0.5)
    try:
        win.control_window('Lista de entregas', timeout=1)
    except Exception as e:
        pass
    else:
        win.send_keys(keys='{ENTER}')


def verificar_entregas():
    control = win.control_window('SAP Business One 10.0 - TDP CORP S.A.')
    desk.click(f'coordinates:{control.left + 150},{control.bottom - 20}', action='right_click')
    win.send_keys(keys='{UP}', send_enter=True)
    if 'No existen registros coincidentes' in desk.get_clipboard_value():
        control = win.control_window('Entrega')
        sleep(0.5)
        desk.click(f'coordinates:{control.right - 10},{control.top + 10}')
        return False
    return True

        
        
def copiar_a_factura():
    sleep(1)
    control = win.control_window('Entrega')
    desk.click(f'coordinates:{control.right - 75},{control.bottom-30}')
    sleep(0.5)
    win.send_keys(keys='{DOWN}{DOWN}')
    sleep(0.5)
    win.send_keys(keys='{ENTER}')
    print('Formulario de factura abierto')
    sleep(0.5)


def crear_comentario():
    control = win.control_window('name:"Factura de deudores" and type:Window')
    desk.click(f'coordinates:{control.left + 150},{control.bottom - 100}', action='right_click')
    sleep(0.5)
    win.send_keys(keys='{DOWN}{DOWN}', send_enter=True)
    sleep(0.5)
    win.send_keys(keys='{CTRL}x')
    comment = desk.get_clipboard_value()
    comment = comment.split('Basado en Entregas')[0]
    comment = f'{comment}  Creador por: Bot'
    win.send_keys(keys=comment)
    sleep(0.5)


def llenar_datos_factura():
    control = win.control_window('id:"30009"')
    desk.click(f'coordinates:{control.right - 50},{control.top + 120}')
    win.send_keys(keys='{TAB}01')
    sleep(0.1)
    win.send_keys(keys='{TAB}F023')
    sleep(0.1)
    win.send_keys(keys='{TAB}')
    sleep(0.1)
    print('Datos de tipo de documento y serie establecidos')

    desk.click(f'coordinates:{control.left + 200},{control.top + 235}', action='right_click')
    sleep(0.5)
    win.send_keys(keys='{DOWN}', send_enter=True)
    fact_export = desk.get_clipboard_value()
    print(fact_export)
    sleep(0.2)
    if fact_export == 'N':
        # Seleccionar venta Ventainterna
        win.send_keys(keys='{TAB}{DOWN}')
        sleep(0.2)
        win.send_keys(keys='{ENTER}')
    else:
        print('las facturas de exportación deben de generar de forma manual')
    print('Datos de tipo de venta establecidos')

    
def get_guias():
    login_sap()
    formulario_de_entregas()
    activar_busqueda()
    parametros_busqueda()
    hay_entrega = verificar_entregas()
    if hay_entrega:
        copiar_a_factura()
        llenar_datos_factura()
        crear_comentario()

    
if __name__ == '__main__':
    try:
        get_guias()
    except Exception as e:
        print(e)
    finally:
        sleep(2)
        #win.close_window('SAP Business One 10.0 - TDP CORP S.A.')
        
    
        
#FE - Tipo de Operación: Ventalnterna
# comentario; eliminar comentario de sistema y agregar comentario de creación de factura
