import datetime

import requests


class Api():
    URL = 'https://api.timeweb.ru/v1.1'

    def __init__(self, token):
        self.token = token

    def request(self, method, params, request_method):
        headers = { "Content-Type": "application/json",
                    "Accept": "application/json",
                    "x-app-key": "rrbrMecQRjzfL9dWaZEqYdrL",
                    "Authorization": "Bearer {}".format(self.token)}

        req_funcs = {
         "GET": requests.get,
         "POST": requests.post,
         "PUT": requests.put,
         "DELETE": requests.delete,
         "OPTIONS": requests.options,
        }

        response = req_funcs[request_method]('{0}/{1}'.format(self.URL, method), headers=headers, json=params)
        return response.text

    @classmethod
    def get_token(self,
                  user: str,
                  password: str) -> str:
        headers = {"Content-Type": "application/json", "Accept": "application/json", "x-app-key": "rrbrMecQRjzfL9dWaZEqYdrL"}
        response = requests.post('https://api.timeweb.ru/v1.1/access', headers=headers, auth=(user, password))

        return response.json()['token']

    def post_comment(self,
                     message: str,
                     user: str,
                     ticket: str,
                     upthread=False) -> str:
        data = {"message": message,
                "attachments": [],
                "internal": True,
                "upthread": upthread}
        method = "accounts/{0}/tickets/{1}/comments".format(user, str(ticket))

        response = self.request(method, data, "POST")
        return response

    def delay_ticket(self,
                     user: str,
                     ticket: str,
                     delay_time: datetime.timedelta,
                     message: str) -> str:
        now = datetime.datetime.now()
        delay_time = format(now + delay_time, '%Y-%m-%d %H:%M:%S')
        data = {"delay": delay_time,
                "delay_comment": message
                }
        method = "accounts/{0}/tickets/{1}".format(user, str(ticket))

        response = self.request(method, data, "PUT")
        return response