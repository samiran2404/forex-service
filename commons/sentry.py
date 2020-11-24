from config import Cfg, constants
import os
from functools import wraps

STAGE = os.environ.get(constants.STAGE)


def app_sentry(function):
    @wraps(function)
    def wrapper(**kwargs):
        try:
            return function(**kwargs)
        except:
            request = kwargs['request']
            headers = kwargs['request'].headers
            CONF = Cfg(STAGE)
            if STAGE != constants.LOCAL:
                CONF.Logger.user_context({
                    'environment': STAGE,
                    'event': request
                })
                CONF.Logger.captureException()
            raise

    return wrapper


def sentry(function):
    @wraps(function)
    def wrapper(event, context):
        try:
            return function(event, context)
        except Exception as e:
            if isinstance(event, list):
                event = event[0]
            CONF = Cfg(STAGE)
            CONF.Logger.user_context({
                'environment': STAGE,
                'event': event,
            })
            CONF.Logger.captureException()
            raise

    return wrapper
