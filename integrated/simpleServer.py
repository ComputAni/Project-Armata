from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time
import json

start = None
end = None

class myServer(BaseHTTPRequestHandler):
	
	def do_POST(self):
		global start, end
                
                print("START")
                contentLen = int(self.headers.getheader('content-length', 0))
                postBody = json.loads(self.rfile.read(contentLen))
                start = (int(postBody['startRow']), int(postBody['startCol']))
                end = (int(postBody['endRow']), int(postBody['endCol']))

                print "Recieved start from iOS: ", start
                print "Recieved end from iOS: ", end


def server_run(server_class=HTTPServer, handler_class=myServer, port=8000):
	global start, end
        server_address = ("", port)
	httpd = server_class(server_address, handler_class)
        httpd.handle_request()

        return start,end


#if __name__ == "__main__":
#	run()

# curl 128.237.233.114:8000 -X POST
