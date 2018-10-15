# -*- coding:utf-8 -*-
import time
import json
import logging
import datetime
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from .BaseHandler import BaseHandler
from ..util.RedisUtil import *
from ..util.RabbitmqUtil import *
from ..config.Config import web_thread

logger = logging.getLogger(__name__)


class MainHandler(BaseHandler):
    """
    Http请求入口
    """
    executor = ThreadPoolExecutor(web_thread)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        result = {"status": 0, "errmsg": "", "payload": []}
        try:
            uri = self.request.uri
            kye_list = uri.split("/")
            if len(kye_list) == 4:
                productkey = kye_list[2]
                data_key = kye_list[3]
            else:
                result = {
                    "status": 400,
                    "errmsg": "INVALID_PARAMS",
                    "payload": []}
                raise Exception()
            check_result, data = ApiSignatureUtil().check_sign(
                "Tornado", self.request, data_key)
            # print(check_result, params)
            if check_result:
                redis_conn = RedisDB()
                rabbit_handel = RabbitMQ_Producer()
                # data_key = self.get_json_argument("data_key")
                # data_resource = self.get_json_argument("data_resource")
                # print(params)
                result = yield self.dealData(data_key, productkey, data, redis_conn, rabbit_handel)
                result = str(result)
            else:
                result = {"status": 3004, "errmsg": "KEY_ERROR", "payload": []}
                return None
                # raise Exception()
        except Exception as err:
            error = str(err)
            logger.error(error)
            result['status'] = 400
            result['payload'] = []
            result['errmsg'] = error
        finally:
            return self.return_response(result)

    @run_on_executor
    def dealData(
            self,
            data_key,
            productkey,
            data,
            redis_conn,
            rabbit_handel):
        """
        :param developer_key:
        :param data_key:
        :param data_resouce:
        :return:
        """
        result = {"status": 0, "errmsg": "", "payload": []}
        try:
            """
            message = {
                        "id": 消息ID,
                        "topic": 消息TOPIC,
                        "type": "data",data：数据类型
                        "dataid": "dataid",datakey
                        "version": "0",0：精简版
                        "accessMode": "1", 1：HTTP访问
                        "payload": parameters,数据内容
                    }
            """

            timestamp = time.mktime(datetime.datetime.now().timetuple())
            data_path = self.get_data_path(data_key, productkey, redis_conn)
            topic = "/data/%s/%s" % (productkey, data_key)
            if data_path:
                message = {'id': timestamp,
                           "topic": topic,
                           'type': 'data',
                           'dataid': data_key,
                           'version': '0',
                           'accessMode': '1',
                           'payload': {
                               'timestamp': timestamp,
                               'productkey': productkey,
                               'params': json.loads(data["parameters"]),
                           },
                           }
                rabbit_broker, channel = rabbit_handel.init_conn(data_key)
                rabbit_handel.message_publish(
                    json.dumps(message), rabbit_broker, channel, data_key)
            else:
                raise Exception("data type does not exist ")
        except Exception as err:
            error = str(err)
            log.error_msg(error)
            result["status"] = 400
            result["errmsg"] = error
        return result

    def get_data_path(self, data_key, productkey, redis_conn):
        """
        :return:
        """
        try:
            redis_result = redis_conn.getData(data_key)
            if redis_result == "":
                return True
                # return False
            else:
                return True
        except Exception as e:
            raise Exception("check_developer_key " + str(e))
