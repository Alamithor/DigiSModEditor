import logging.config


logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] [%(levelname)s] [%(module)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'detailed': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s: %(module)s: %(lineno)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[%(asctime)s] [%(levelname)s] - %(message)s',
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'DigiSModEditor.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 7,
        },
        'thread': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filename': 'DigiSModEditor.threads.log',
            'maxBytes': 3145728,  # 3MB
            'backupCount': 2,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
    'loggers': {
        'DigiSModEditor': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'DigiSModEditor.threads': {
            'level': 'DEBUG',
            'handlers': ['thread'],
            'propagate': False
        },
    }
}

logging.config.dictConfig(logging_config)
