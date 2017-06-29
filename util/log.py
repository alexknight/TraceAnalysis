# coding:utf-8
import os
import logging
import logging.config as log_conf

from config import config

log_dir = os.path.dirname(os.path.dirname(__file__))+'/logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

log_path = os.path.join(log_dir, 'run.log')

log_config = {
    'version': 1.0,
    'formatters': {
        'detail': {
            'format': '%(asctime)s - %(name)s - %(levelname)s  - [%(filename)s:%(lineno)s]: %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detail'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 10,
            'filename': log_path,
            'level': 'DEBUG',
            'formatter': 'detail',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'online': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'debug': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }
}


def logger():
    log_conf.dictConfig(log_config)

    return logging.getLogger(config.LOG_LEVEL)
