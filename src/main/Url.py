from .handler.BaseHandler import url_wrapper
from .handler.MainHandler import MainHandler

handler = url_wrapper([
    (r"/", MainHandler),
])
