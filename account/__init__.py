import logging
 
logging.basicConfig(
    filename="api.log",
    format='%(asctime)s %(message)s',
    filemode='w'
)

logger = logging.getLogger()