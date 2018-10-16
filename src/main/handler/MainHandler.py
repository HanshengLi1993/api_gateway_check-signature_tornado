# -*- coding:utf-8 -*-
import time
import random
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from .BaseHandler import BaseHandler
from ..util.RedisUtil import *
from ..util.RabbitmqUtil import *
from ..util.CheckSignatureUtil import *
from ..util.PrpcryptUtil import *
from ..config.Config import *

logger = LogUtil()
SystemHeader = SystemHeader()


class MainHandler(BaseHandler):
    """
    Http请求入口
    """
    executor = ThreadPoolExecutor(web_thread)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        result = None
        try:
            checkResult = yield self.__checkRequest(self.request)
            if checkResult:
                result = {"status": 0, "errmsg": "", "payload": []}
            else:
                result = {"status": 3004, "errmsg": "KEY_ERROR", "payload": []}
        except Exception as err:
            error = str(err)
            logger.error(error)
            result = {"status": 400, "errmsg": error, "payload": []}
        finally:
            return self.return_response(result)

    @run_on_executor
    def __checkRequest(self, request):
        """
        :param request:
        :param redis_conn:
        :param rabbit_handler:
        :return:
        """
        result = False
        try:
            headers = request.getHeaders()
            message = request.getBodys()
            appKey = headers[SystemHeader.X_CA_KEY]
            timestamp = headers[SystemHeader.X_CA_TIMESTAMP]
            nonce = headers[SystemHeader.X_CA_NONCE]
            nowTimestamp = int(time.time() * 1000)
            if nowTimestamp - 900000 <= int(timestamp) <= nowTimestamp + 900000:
                prpcrypt_handler = PrpcryptUtil(prpcrypt_key)
                if self.__checkNonce(nonce, prpcrypt_handler):
                    if CheckSignatureUtil().checkSignature(request):
                        self.__setNonce(nonce, timestamp, prpcrypt_handler)
                        self.__pubilshMessage(appKey, message, prpcrypt_handler)
                        return True
        except Exception as err:
            error = str(err)
            logger.error(error)
        finally:
            return result

    def __checkNonce(self, nonce, prpcrypt_handler):
        try:
            redisHandler = RedisDB(redis_host, redis_port, prpcrypt_handler.decrypt(redis_passowrd))
            if redisHandler:
                if redisHandler.getString(nonce):
                    return False
                else:
                    return True
            else:
                raise Exception("redis connection fail")
        except Exception as err:
            error = str(err)
            logger.error(error)

    def __setNonce(self, nonce, timestamp, prpcrypt_handler):
        try:
            redisHandler = RedisDB(redis_host, redis_port, prpcrypt_handler.decrypt(redis_passowrd))
            if redisHandler:
                expire = random.randint(1, 60000) + 900000
                redisHandler.setString(nonce, timestamp, xx=expire)
            else:
                raise Exception("redis connection fail")
        except Exception as err:
            error = str(err)
            logger.error(error)

    def __pubilshMessage(self, appKey, message, prpcrypt_handler):
        try:
            rabbit_handler = RabbitmqProducer(rabbitmq_host, rabbitmq_port, rabbitmq_user, prpcrypt_handler.decrypt(rabbitmq_password), exchangeName, queueName, routeKey)
            if rabbit_handler:
                pass
            else:
                raise Exception("rabbitmq connection fail")
            rabbit_broker, channel = rabbit_handler.init_conn(appKey)
            rabbit_handler.message_publish(message, rabbit_broker, channel, appKey)
        except Exception as err:
            error = str(err)
            logger.error(error)
