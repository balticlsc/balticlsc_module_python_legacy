import logging
logging.basicConfig(level=logging.DEBUG, format='## SERVER.TASKMGR ## %(asctime)s.%(msecs)03d ## %(levelname)s|%(name)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
logger = logging.getLogger('api')
