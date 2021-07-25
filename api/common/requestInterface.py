import json

import requests
from requests import Timeout, RequestException
from time import time
import logging

logger = logging.getLogger('log')


class RequestInterface:
    """
        GET：    请求指定的页面信息，并返回实体主体。
        HEAD：   只请求页面的首部。
        POST：   请求服务器接受所指定的文档作为对所标识的URI的新的从属实体。
        PUT：    从客户端向服务器传送的数据取代指定的文档的内容。
        DELETE： 请求服务器删除指定的页面。
    """

    def __init__(self, method, url, headers, data=None):
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data

    def get(self, url, headers, timeout=(3, 7)):
        res = requests.get(url, headers=headers)
        return res

    def post(self, url, headers, data):
        res = requests.post(url, headers=headers, json=data)
        # files = {"file": open(data['path'], "rb")}
        # res = requests.post(url, params=params, files=files, headers=headers)
        return res

    def delete(self, url, headers, data):
        res = requests.delete(url, headers=headers, json=data)
        return res

    def put(self, url, headers, data):
        res = requests.put(url, headers=headers, json=data)
        return res

    def main(self):
        startTime = time()
        res = None
        self.data = json.loads(self.data) if type(self.data) == str else self.data
        status_code = None
        try:
            if self.method == "GET":
                res = self.get(self.url, self.headers)

            elif self.method == 'POST':
                res = self.post(self.url, self.headers, self.data)

            elif self.method == 'DELETE':
                res = self.delete(self.url, self.headers, self.data)

            elif self.method == 'PUT':
                res = self.put(self.url, self.headers, self.data)

            # 响应延迟，毫秒ms
            duration = int(round(time() - startTime, 3) * 1000)
            # 响应头
            response_headers = res.headers
            # 响应HTTP状态码
            status_code = res.status_code
            # 响应体
            response_body = res.json()
            # 返回响应延迟、响应头、status_code、响应体
            return (response_headers, response_body, duration, status_code, self.data)
        except Timeout as e:
            return {'code': 1001, 'data': '请求超时:%s' % e}
        except RequestException as e:
            return {'code': 1001, 'data': '请求异常:%s' % e}
        except Exception as e:
            if status_code == 418:
                return {'code': 1001, 'data': '{0}，遭到网站的反爬程序'.format(str(status_code))}
            return {'code': 1001, 'data': '{0}，出错原因:{1}'.format(str(status_code), e)}
