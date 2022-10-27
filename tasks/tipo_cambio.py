from time import sleep
from Browser import Browser
from Browser.utils.data_types import SupportedBrowsers
from RPA.Windows import Windows
from login import login_sap
from RPA.Desktop import Desktop
from robot.api.deco import keyword

desktop = Desktop()
b = Browser(timeout="20 s", retry_assertions_for="500 ms")
win = Windows()

WINDOWS_NAME = 'SAP Business One 10.0 - TDP CORP S.A.'


def get_tipo_cambio():
    b.new_browser(browser=SupportedBrowsers.chromium)
    b.new_context(
        acceptDownloads=True,
        viewport={'width': 1920, 'height': 1080},
    )
    b.new_page('https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx')
    tipo_cambio = b.get_text('#ctl00_cphContent_rgMercadoProfesional_ctl00__0 td:last-child')
    b.close_browser()
    return tipo_cambio


@keyword('Tipo de Cambio')
def tipo_cambio():
    login_sap()
    tipo_cambio = get_tipo_cambio()
    print(f'Tipo de cambio: {tipo_cambio}')
    sleep(10)
    win.control_window(WINDOWS_NAME)
    win.send_keys(keys='{Ctrl}{F3}')
    win.control_window('Formulario de búsqueda principal')
    win.get_element('type:Edit')
    win.send_keys(keys='Tipos de cambio', send_enter=True)
    win.send_keys(keys=tipo_cambio, send_enter=True)
    win.close_window(WINDOWS_NAME)
    return tipo_cambio


#if __name__ == '__main__':
#    tipo_cambio()