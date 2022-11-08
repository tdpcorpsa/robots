from re import S
from .login import login_sap
from RPA.Windows import Windows
from time import sleep
from datetime import datetime
from RPA.Desktop import Desktop


win = Windows()
desk = Desktop()


def formulario_de_pedidos():
    win.control_window('Formulario de búsqueda principal')
    win.send_keys(keys='{Ctrl}{F3}')
    win.send_keys(keys='Orden de venta', send_enter=True)
    print('Formulario de orden de venta abierto')
    sleep(1)

    
def activar_busqueda():
    try:
        win.control_window('Orden de venta')
    except Exception as e:
        raise Exception('No se encuentra el formulario de orden de venta')   

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
    # Estado Avierto
    win.send_keys(keys='{TAB}{DOWN}')
    sleep(0.2)
    win.send_keys(keys='{DOWN}{ENTER}')
    sleep(0.1)
    win.send_keys(keys='{TAB}')
    sleep(0.1)
    # Fecha de contabilización
    #fecha = datetime.now().strftime('%d/%m/%Y')
    #win.send_keys(keys=fecha)
    #sleep(0.1)
    #win.send_keys(keys='{TAB}')
    #sleep(0.1)

    # Automático
    control = win.control_window('name:"Campos: Parametriz..."  and type:Window')
    desk.click(f'coordinates:{control.left + 200},{control.top + 40}')
    sleep(0.1)
    win.send_keys(keys='{ENTER}')

    # Tipo de pedido pedido
    control = win.control_window('name:"Campos: Parametriz..."  and type:Window')
    desk.click(f'coordinates:{control.left + 200},{control.top + 190}')
    sleep(0.1)
    win.send_keys(keys='{DOWN}', send_enter=True)

    #control = win.control_window('name:"Entrega" and type:Window')
    #desk.click(f'coordinates:{control.left + 200},{control.top + 90}')

    print('Parametros de busqueda establecidos')
    sleep(0.1)
    win.send_keys(keys='{ENTER}')
    sleep(0.5)
    try:
        control = win.control_window('name:"Lista de Pedidos de cliente" and type:Window', timeout=1)
    except Exception as e:
        pass
    else:
        win.send_keys(keys='{ENTER}')


def verificar_pedido():
    control = win.control_window('SAP Business One 10.0 - TDP CORP S.A.')
    desk.click(f'coordinates:{control.left + 150},{control.bottom - 20}', action='right_click')
    win.send_keys(keys='{UP}', send_enter=True)
    if 'No existen registros coincidentes' in desk.get_clipboard_value():
        control = win.control_window('Orden de venta')
        sleep(0.5)
        desk.click(f'coordinates:{control.right - 10},{control.top + 10}')
        return False
    return True

        
        
def copiar_a_factura():
    sleep(1)
    control = win.control_window('Orden de venta [Autorizado]')
    desk.click(f'coordinates:{control.right - 75},{control.bottom-30}')
    sleep(0.5)
    win.send_keys(keys='{DOWN}{DOWN}')
    sleep(0.5)
    win.send_keys(keys='{ENTER}')
    print('Formulario de factura abierto')
    sleep(0.5)
    desk.click(f'coordinates:{control.right - 10},{control.top+10}')
    return win.control_window('name:"Factura de reserva de clientes" and type:Window')


def crear_comentario():
    control = win.control_window('name:"Factura de reserva de clientes" and type:Window')
    desk.click(f'coordinates:{control.left + 150},{control.bottom - 100}', action='right_click')
    sleep(0.1)
    win.send_keys(keys='{DOWN}{DOWN}', send_enter=True)
    sleep(0.1)
    win.send_keys(keys='{CTRL}x')
    comment = desk.get_clipboard_value()
    comment = comment.split('Basado en')[0]
    comment = f'{comment}  Creado por: Bot'
    desk.set_clipboard_value(comment)
    win.send_keys(keys='{CTRL}v')
    sleep(0.1)


def llenar_datos_factura():
    control = win.control_window('name:"Campos: Parametriz..." and and type:Window')
    desk.click(f'coordinates:{control.right - 50},{control.top + 45}')
    win.send_keys(keys='01')
    sleep(0.1)
    win.send_keys(keys='{TAB}F023')
    sleep(0.1)
    win.send_keys(keys='{TAB}')
    win.send_keys(keys='{TAB}')
    win.send_keys(keys='{DOWN}', send_enter=True)
    sleep(0.1)
    win.send_keys(keys='{TAB}')
    win.send_keys(keys='{CTRL}c')
    fact_export = desk.get_clipboard_value()
    print(fact_export)
    sleep(0.1)
    if fact_export == 'Y':
        print('las facturas de exportación deben de generar de forma manual')
        sleep(0.5)
        # cerramos formulario
        control = win.control_window('name:"Factura de reserva de clientes" and type:Window')
        desk.click(f'coordinates:{control.right - 10},{control.top+10}')
        raise Exception('las facturas de exportación deben de generar de forma manual')
 
    print('Datos de tipo de venta establecidos')


def crear_factura():
    control = win.control_window('name:"Factura de reserva de clientes" and type:Window')
    desk.click(f'coordinates:{control.left + 50},{control.bottom - 25}')
    sleep(0.1)
    win.send_keys(keys='{ENTER}')
    sleep(10)
    desk.click(f'coordinates:{control.right - 10},{control.top + 10}')

    
def proceso_creacion_factura():
    login_sap()
    formulario_de_pedidos()
    activar_busqueda()
    parametros_busqueda()
    hay_pedido = verificar_pedido()
    if hay_pedido:
        copiar_a_factura()
        llenar_datos_factura()
        crear_comentario()
        crear_factura()
        proceso_creacion_factura()


def job():
    try:
        proceso_creacion_factura()
    except Exception as e:
        print(e)
    finally:
        sleep(2)
        #win.close_window('SAP Business One 10.0 - TDP CORP S.A.')
        
