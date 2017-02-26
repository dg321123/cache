import logging
logger = logging.getLogger('cacher_log')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('cacher.log', mode='w')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
