import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from main.Url import handler
from main.config.Config import DEBUG_MODE
from tornado.options import define, options




define("port", default=8080, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = handler
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=DEBUG_MODE,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    # http_server = tornado.httpserver.HTTPServer(Application(), ssl_options={
    #     "certfile": os.path.join(os.path.abspath("."), "server.crt"),
    #     "keyfile": os.path.join(os.path.abspath("."), "server.key"),
    # })

    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
