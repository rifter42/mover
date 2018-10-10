import http.server
import json
import os
import subprocess

import yaml

MOVER_HOME = "/home/mover"

class ConfigHandler(http.server.BaseHTTPRequestHandler):

    """
    Обработчик post-запросов от панели
    """

    def create_config(self, data: dict):

        """
        делает из полученного json конфиг в yaml
        :param data:
        :return:
        """

        with open(self.path, 'w') as f:
            yaml.dump(data, f, allow_unicode=True)

    def run_mover(self, path: str):
        mover_path = os.path.join(MOVER_HOME, "main.py")
        subprocess.Popen(["python3", mover_path, "-c", path])


    def do_GET(self):

        """
        ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯ ¯\_(ツ)_/¯
        """

        self.send_response(http.HTTPStatus.OK)
        self.end_headers()
        self.wfile.write("ebat ti loh")

    def do_POST(self):

        """
        Обрабатывает запрос и запускает в отдельном процессе переносатор
        :return:
        """

        post_data = str(self.rfile.read(int(self.headers['Content-Length'])), "UTF-8")

        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_response(http.HTTPStatus.OK)
        self.end_headers()

        data = json.loads(post_data)
        self.log_request()
        self.log_message(post_data)
        path = os.path.join(MOVER_HOME, "configs/{}_config.yaml".format(list(data.keys())[0]))
        self.create_config(data)
        self.run_mover(path)



def run_server(server_class=http.server.HTTPServer, handler_class=ConfigHandler, port=1488):

    """
    :param server_class:
    :param handler_class:
    :param port:
    :return:
    """

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
