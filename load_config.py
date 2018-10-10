import json
import http.server
from http.server import SimpleHTTPRequestHandler
import ssl
from pprint import pprint
import logging
from logging import getLogger
import yaml
import subprocess

class PostHandler(http.server.BaseHTTPRequestHandler):
	def create_config(self, data):
		with open(self.path, 'w') as f:
			yaml.dump(data, f, allow_unicode=True)

	def run_mover(self):
		subprocess.Popen(["python3", "/home/mover/main.py", "-c", self.path])

	def do_POST(self):
		self.post_data = str(self.rfile.read(int(self.headers['Content-Length'])), "UTF-8")
		self.send_header("Access-Control-Allow-Origin", "*")
		self.send_response(200)
		self.end_headers()
		data = json.loads(self.post_data)
		self.log_request()
		self.log_message(self.post_data)
		self.path = "/home/mover/configs/{}_config.yaml".format(list(data.keys())[0])
		self.create_config(data)
		self.run_mover()
	


def run_server(server_class=http.server.HTTPServer, handler_class=PostHandler, port=1488):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()

if __name__ == '__main__':
	run_server()
