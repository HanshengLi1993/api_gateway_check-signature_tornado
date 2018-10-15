# -*- coding:utf-8 -*-
import os

# rabbitmq
rabbitmq_host = "1.1.1.1"
rabbitmq_port = 31861
rabbitmq_user = "root"
rabbitmq_password = "367b61b333c242a4253cfacfe6ea709f"  # 0123456789ABCDEF
exchangeName = "rule_engine"
queueName = "rule_engine"
routeKey = "rule_engine.event"

# redis
redis_host = "1.1.1.1"
redis_port = 6379
redis_passowrd = "367b61b333c242a4253cfacfe6ea709f"  # 0123456789ABCDEF

# log
log_path = "/var/log/api_gateway_check_signature_tornado"
log_name = "mysite.log"
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            # 当达到10MB时分割日志
            'maxBytes': 1024 * 1024 * 10,
            # 最多保留50份文件
            'backupCount': 50,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': os.path.join(log_path, log_name),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'debug': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

# web
web_thread = 10

# prpcrypt
key = "keyskeyskeyskeys"

# debug mode
DEBUG_MODE = False
