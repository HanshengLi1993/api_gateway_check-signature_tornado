# -*- coding:utf-8 -*-
from urllib import parse
from .SignUtil import *
from .LogUtil import *
from ..Request import *
from .RedisUtil import *
from .PrpcryptUtil import *
from ..config.Config import redis_host, redis_port, redis_passowrd, prpcrypt_key


class CheckSignatureUtil:
    """
    签名校验工具
    """

    def __init__(self):
        self.__Constants = Constants()
        self.__HttpHeader = HttpHeader()
        self.__SystemHeader = SystemHeader()
        self.__logger = LogUtil()
        self.__redis = RedisDB(redis_host, redis_port, PrpcryptUtil(prpcrypt_key).decrypt(redis_passowrd))

    def __tornado_request_handler(self, request, *args, **kwargs):
        """Get arguments from Tornado"""
        __request = Request()
        try:
            headers = request.headers
            __request.setMethod(request.method)
            __request.setHost(request.host)
            __request.setPath(request.path)
            __request.setAppKey(headers['X-Ca-Key'])
            __request.setAppSecret(self.__getAppSecret(headers['X-Ca-Key']))
            __request.setTimeout(self.__Constants.DEFAULT_TIMEOUT)
            __request.setHeaders(headers)
            __request.setQuerys(request.query)
            __request.setBodys(request.body)
            __request.setSignHeaderPrefixList(self.__getSignHeaderPrefixList(headers))
        except Exception as err:
            error = str(err)
            self.__logger.error(error)
        finally:
            return __request

    def __percentEncodeRfc3986(self, s):
        out = None
        try:
            if len(s) > 0:
                """quote_plus 保证某些字符如'/'等也会被URL编码"""
                out = parse.quote_plus(s, encoding=self.__Constants.ENCODING) \
                    .replace("+", "%20") \
                    .replace("*", "%2A") \
                    .replace("%7E", "~")
            else:
                pass
        except Exception:
            out = s
        finally:
            return out

    def __getAppSecret(self, AppKey):
        return self.__redis.getString(AppKey)

    def __getSignHeaderPrefixList(self, headers):
        default_header = (self.__HttpHeader.HTTP_HEADER_ACCEPT,
                          self.__HttpHeader.HTTP_HEADER_CONTENT_MD5,
                          self.__HttpHeader.HTTP_HEADER_CONTENT_TYPE,
                          self.__HttpHeader.HTTP_HEADER_DATE,
                          self.__HttpHeader.HTTP_HEADER_USER_AGENT,
                          self.__SystemHeader.X_CA_KEY,
                          self.__SystemHeader.X_CA_NONCE,
                          self.__SystemHeader.X_CA_SIGNATURE,
                          self.__SystemHeader.X_CA_SIGNATURE_HEADERS,
                          self.__SystemHeader.X_CA_TIMESTAMP)
        header_list = headers.keys()
        for header, value in headers.items():
            if header in default_header:
                header_list.remove(header)
        return header_list

    def checkSignature(self, request, *args, **kwargs):
        try:
            __request = self.__tornado_request_handler(request, *args, **kwargs)
            if __request:
                headers = request.getHeaders()
                signature_request = headers[self.__SystemHeader.X_CA_SIGNATURE]
                headers.pop(self.__SystemHeader.X_CA_SIGNATURE)
                request.setHeaders(headers)

                signature_recount = SignUtil().sign(request.getAppSecret(), request.getMethod(), request.getPath(), request.getHeaders(),
                                                    request.getQuerys(), request.getBodys(), request.getSignHeaderPrefixList())
                if hmac.compare_digest(signature_request, signature_recount):
                    return True
                else:
                    return False
            else:
                return False
        except Exception as err:
            error = str(err)
            self.__logger.error(error)
