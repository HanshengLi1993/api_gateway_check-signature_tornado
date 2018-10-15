# -*- coding:utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
from datetime import date, datetime
from importlib import import_module
from tornado.escape import url_unescape


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Header", "x-requested-width")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")
        self.set_header('Content-Type', 'application/json,charset=UTF-8')

    def return_response(self, content):
        self.write(json.dumps(content, cls=CJsonEncoder))
        self.finish()

    def get_json_argument(self, name, default=None):
        data = bytes.decode(self.request.body)
        arg_list = data.split("&")
        if len(arg_list) > 1:
            for arg in arg_list:
                key, value = arg.split("=")
                if name == key:
                    return url_unescape(value, encoding='utf-8', plus=True)
                elif default is not None:
                    return default
        else:
            return url_unescape(arg_list, encoding='utf-8', plus=True)


def include(module):
    res = import_module(module)
    urls = getattr(res, 'urls', res)
    return urls


def url_wrapper(urls):
    wrapper_list = []
    for url in urls:
        path, handles = url
        if isinstance(handles, (tuple, list)):
            for handle in handles:
                pattern, handle_class = handle
                wrap = ('{0}{1}'.format(path, pattern), handle_class)
                wrapper_list.append(wrap)
        else:
            wrapper_list.append((path, handles))
    return wrapper_list
