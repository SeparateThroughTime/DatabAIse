import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -%(levelname)s -on line: %(lineno)d -%(message)s')

logger = logging.getLogger('name')
logger.debug('hello')
logger.warning("warn")