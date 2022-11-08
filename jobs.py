import schedule
import time
from tasks import crear_factura_deudores
import logging


logging.basicConfig()
schedule_logger = logging.getLogger('schedule')
schedule_logger.setLevel(level=logging.DEBUG)


schedule.every(1).to(5).minutes.do(crear_factura_deudores.job)

while True:
    schedule.run_pending()
    time.sleep(1)

