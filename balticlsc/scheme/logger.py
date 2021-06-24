import logging
import os

SYS_MODULE_NAME = os.getenv('SYS_MODULE_NAME', 'BalticLSC module')
logging.basicConfig(level=logging.DEBUG, format='## '+SYS_MODULE_NAME+' ## %(asctime)s.%(msecs)03d ## %(levelname)s|%(name)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
logger = logging.getLogger('api')
