import settings
import socketserver
import handler


class MyThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    request_queue_size = settings.REQUEST_QUEUE_SIZE


def runserver():
    with MyThreadingTCPServer(
            (settings.HOST, settings.PORT),
            settings.HANDLER
    ) as httpd:
        httpd.handle_request()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            print("Server was interrupted by user.")
