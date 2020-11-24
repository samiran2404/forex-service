from common.sentry import sentry
from zappa import handler
from tools.service import forex
import logging
import os
from config import Cfg, constants

CONF = Cfg(os.environ.get(constants.STAGE))


@sentry
def lambda_handler(event, context):
    logging.info('Event received by forex service')
    loader = forex(CONF)
    loader.process()
    return handler.lambda_handler(event, context)
