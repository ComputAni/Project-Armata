from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time

class myServer(BaseHTTPRequestHandler):
	
	def do_POST(self):
		print("START")


def run(server_class=HTTPServer, handler_class=myServer, port=8000):
	server_address = ("", port)
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()


if __name__ == "__main__":
	run()

# curl 128.237.233.114:8000 -X POST
