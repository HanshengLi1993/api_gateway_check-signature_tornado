# -*- coding:utf-8 -*-
from urllib import parse
from .SignUtil import *
from .LogUtil import *


class CheckSignatureUtil:
    """
    签名校验工具
    """

    def __init__(self):
        self.__Constants = Constants()
        self.__logger = LogUtil()

    def __tornado_request_handler(self, request, *args, **kwargs):
        """Get arguments from Tornado"""
        method = uri = ""
        params = {}
        try:
            uri = request.protocol + "://" + request.host + request.path
            method = request.method
            params = request.arguments
            if len(request.arguments) > 0:
                parameters = {}
                for key, value in params.items():
                    part = self.__percentEncodeRfc3986(bytes.decode(value[0]))
                    parameters[key] = part
                params = parameters
            else:
                parameters = {}
                params = bytes.decode(request.body)
                arg_list = params.split("&")
                if len(arg_list) > 1:
                    for arg in arg_list:
                        key, value = arg.split("=")
                        parameters[key] = parse.unquote_plus(
                            value, encoding=self.__Constants.ENCODING)
                    params = parameters
                    # print(params, uri, method)
        except Exception as err:
            error = str(err)
            self.__logger.error(error)
        finally:
            return method, uri, params

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

    def check_signature(self, request, client_id, *args, **kwargs):
        request_method = request_uri = ""
        params = {}
        try:
            if framework == "Django":
                request_method, request_uri, params = self.__djando_request_handler(
                    request, *args, **kwargs)
            elif framework == "Tornado":
                request_method, request_uri, params = self.__tornado_request_handler(
                    request, *args, **kwargs)
            elif framework == "Flask":
                pass
            else:
                pass
            # print(request_method, request_uri, params)
            if "signature" in params.keys():
                sign_old = params["signature"]
                params.pop("signature")
            else:
                return False
            sign_check = self.sign(
                request_method, request_uri, params, client_id)
            # print("sign_check", sign_check, sign_old)
            if hmac.compare_digest(sign_old, sign_check):
                # check pass
                return True, params
            else:
                # check fail
                return False, params
        except Exception as err:
            error = str(err)
            self.log.error_msg(error)
