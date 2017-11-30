from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time
import json


class myServer(BaseHTTPRequestHandler):
	
	def do_POST(self):
		global msgReceived
                
                print("START")
                contentLen = int(self.headers.getheader('content-length', 0))
                postBody = json.loads(self.rfile.read(contentLen))
                start = (postBody['startRow'], postBody['startCol'])
                end = (postBody['endRow'], postBody['endCol'])

                print "Start", start
                print "End", end


def run(server_class=HTTPServer, handler_class=myServer, port=8000):
	global msgReceived
        server_address = ("", port)
	httpd = server_class(server_address, handler_class)
        httpd.handle_request()


if __name__ == "__main__":
	run()

# curl 128.237.233.114:8000 -X POST
