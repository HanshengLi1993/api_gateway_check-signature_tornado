# -*- coding:utf-8 -*-
import redis
from .LogUtil import *


class RedisDB:
    """
    Redis操作工具
    """

    def __init__(self, host, port, password):
        self.__host = host
        self.__port = port
        self.__password = password
        self.__redisObj = None
        self.__logger = LogUtil()

    def __open(self):
        try:
            """
            连接池：
                当程序创建数据源实例时，系统会一次性创建多个数据库连接，并把这些数据库连接保存在连接池中，当程序需要进行数据库访问时，
                无需重新新建数据库连接，而是从连接池中取出一个空闲的数据库连接.
            """
            pool = redis.ConnectionPool(host=self.__host, port=self.__port, db=0, password=self.__password)
            self.__redisObj = redis.Redis(connection_pool=pool)
            # self.__redisObj = redis.StrictRedis(host=self.__host,port=self.__port)
        except Exception as err:
            self.__redisObj = None
            self.__logger.error(str(err))

    def setString(self, key, value, xx=None):
        """
        在Redis中设置值，默认，不存在则创建，存在则修改
        :param key:
        :param value:
        :param ex:过期时间（秒）
        :return:
        """
        self.__open()
        try:
            if self.__redisObj != None:
                self.__redisObj.set(name=key, value=value, xx=xx)
        except Exception as err:
            self.__logger.error(str(err))

    def getString(self, key):
        self.__open()
        buf = ""
        try:
            if self.__redisObj != None:
                buf = self.__redisObj.get(name=key).decode("utf-8")
        except Exception as err:
            buf = ""
        return buf
