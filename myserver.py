# Author: Nonidh Singh

from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from sys import argv

class Myserver(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        temp = self.path.strip('/')
        print(temp)
        temp = open(temp,'r')
        self._set_response()
        self.wfile.write(temp.read().encode())
        return 
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print("POSTED DATA:",post_data.decode())
        self._set_response()
        self.wfile.write("POST request sent".encode())

if __name__ == '__main__':
    PORT = 20103
    if(argv[1] != None):
        PORT = int(argv[1])
    s = socketserver.ThreadingTCPServer(("", PORT),Myserver)
    s.allow_reuse_address = True
    print ("Serving on port", PORT)
    s.serve_forever()
