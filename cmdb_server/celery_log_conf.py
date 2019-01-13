# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    celery_log_conf
   Description :
   Author :       fred
   date：         2019-01-02
-------------------------------------------------
   Change Activity:
                  2019-01-02:
-------------------------------------------------
"""
import logging.config
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'celeryformat': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': 'asctime:%(asctime)s name:%(name)s levelname:%(levelname)s filename:%(filename)s module:%(module)s funcName:%(funcName)s lineno:%(lineno)d message:%(message)s - process:%(process)d'
        },
        'djangoformat': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': 'asctime:%(asctime)s name:%(name)s levelname:%(levelname)s filename:%(filename)s module:%(module)s funcName:%(funcName)s lineno:%(lineno)d message:%(message)s - process:%(process)d'
        },
    },
    'handlers': {
        'celery': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份份数
            'formatter': 'celeryformat',  # 使用哪种formatters日志格式
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/celery_logging_take.log',

        },
        'django': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份份数
            'formatter': 'djangoformat',  # 使用哪种formatters日志格式
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/djangoserver.log',
        },
    },
    'loggers': {
        'celery_default': {
            'handlers': ['celery'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django_default': {
            'handlers': ['django'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


logging.config.dictConfig(LOG_CONFIG)
