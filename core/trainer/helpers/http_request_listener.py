"""
Inspired from Nathan Hamiel's work
https://gist.github.com/huyng/814831
"""
import json
import urllib
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from helpers.message_dispatcher import MessageDispatcher
from utils.commons import print_internals
from utils.killable_thread import KillableThread
from core.trainer.local_model.forum_content_handler import ForumContentHandler


class RequestHandler(BaseHTTPRequestHandler):

    BaseHTTPRequestHandler.forum_content = ForumContentHandler()

    """
    Handler for GET HTTP requests. Allows to check if a /closed is called, send the required data to the backend
    through MQTT, stop the server and reinitialize variables.
    """
    def do_GET(self):
        
        request_path = self.path
        
        if request_path == "/closed":
            print_internals("[TRAINER - LISTENER] closing...")
            data = BaseHTTPRequestHandler.forum_content.fill_json()
            MessageDispatcher().send_one_json(json.dumps(data))
            # Killing the server and cleaning handler's data structures (doesn't get garbage collected)
            self.server.running = False
            BaseHTTPRequestHandler.forum_content.reset()

    """
    Handler for POST HTTP requests. Allows to receive data from a crafted page that generates information regarding
    forum and subforum structure.
    """
    def do_POST(self):
        
        request_path = self.path
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        data = self.rfile.read(length)
        # Sent data might be single or multiple
        if data.split("&").__len__() == 1:
            # Removing the name of the field with split, taking the value with the array access, transforming escaped
            # chars into normal and replacing + with spaces.
            data = urllib.unquote(data.split("=", 1)[1].replace("+", " "))
            BaseHTTPRequestHandler.forum_content.handle_request(request_path, data)
        else:
            elements = []
            for element in data.split("&"):
                element = urllib.unquote(element)
                elements.append(element.split("=", 1)[1].replace("+", " "))
            BaseHTTPRequestHandler.forum_content.handle_request(request_path, elements)
        self.send_response(200)

    # do_PUT = do_POST
    # do_DELETE = do_GET


class HTTPRequestListener:

    """
    Instances an HTTPServer with a custom handler (RequestHandler), served inside of a KillableThread
    """
    def __init__(self):
        self._port = 8080
        self._server = HTTPServer(('0.0.0.0', self._port), RequestHandler)
        self._thread = KillableThread(target=self.run)
        self._thread.deamon = True
        print_internals("[TRAINER - LISTENER] Listening on localhost:" + str(self._port))

    def run(self):
        self._server.running = True
        while self._server.running:
            self._server.handle_request()

    def start(self):
        self._thread.start()

    def shut_down(self):
        self._thread.terminate()

