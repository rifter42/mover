import datetime

import requests


class Api():
    URL = 'https://api.timeweb.ru/v1.1'

    def __init__(self, token):
        self.token = token

    def __request(self, method: str, params: dict, request_method: str) -> str:
        """
        Метод для отправки запросов в api
        :param method: метод api
        :param params: параметры запроса
        :param request_method: HTTP метод
        :return:
        """
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
        """
        Получение токена для работы с api.
        :param user:
        :param password:
        :return:
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json", "x-app-key": "rrbrMecQRjzfL9dWaZEqYdrL"}
        response = requests.post('https://api.timeweb.ru/v1.1/access', headers=headers, auth=(user, password))

        return response.json()['token']

    def post_comment(self,
                     message: str,
                     user: str,
                     ticket: str,
                     upthread=False) -> str:
        """
        Добавление комментария к тикету
        :rtype: str
        :param message: текст комментария
        :param user: логин пользователя
        :param ticket: номер тикета строкой
        :param upthread: нужно ли поднимать тикет
        :return:
        """
        data = {"message": message,
                "attachments": [],
                "internal": True,
                "upthread": upthread}
        method = "accounts/{0}/tickets/{1}/comments".format(user, str(ticket))

        response = self.__request(method, data, "POST")
        return response

    def delay_ticket(self,
                     user: str,
                     ticket: str,
                     delay_time: datetime.timedelta,
                     message: str) -> str:
        """
        Откладывание тикета
        :param user: логин пользователя
        :param ticket: номер тикета
        :param delay_time: время, на которое тикет нужно отложить
        :param message: текст комментария
        :return:
        """
        now = datetime.datetime.now()
        delay_time = format(now + delay_time, '%Y-%m-%d %H:%M:%S')
        data = {"delay": delay_time,
                "delay_comment": message
                }
        method = "accounts/{0}/tickets/{1}".format(user, str(ticket))

        response = self.__request(method, data, "PUT")
        return response