from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time
import json

iOSStart = None
iOSEnd = None

class myServer(BaseHTTPRequestHandler):
	
	def do_POST(self):
		global iOSStart, iOSEnd
                
                print("START")
                contentLen = int(self.headers.getheader('content-length', 0))
                postBody = json.loads(self.rfile.read(contentLen))
                iOSStart = (int(postBody['startRow']), int(postBody['startCol']))
                iOSEnd = (int(postBody['endRow']), int(postBody['endCol']))

                print "Recieved start from iOS: ", iOSStart
                print "Recieved end from iOS: ", iOSEnd


def server_run(server_class=HTTPServer, handler_class=myServer, port=8000):
	global iOSStart, iOSEnd
        server_address = ("", port)
	httpd = server_class(server_address, handler_class)
        httpd.handle_request()
        print "server_run :", iOSStart, iOSEnd
        return iOSStart, iOSEnd


#if __name__ == "__main__":
#	run()

# curl 128.237.233.114:8000 -X POST
