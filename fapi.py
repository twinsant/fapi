import urllib
from json import JSONDecodeError
import re

import requests

class Action:
    def __init__(self, api, method, action):
        self.endpoint = api.endpoint
        self.bearer = api.bearer
        self.kwargs = api.kwargs
        self.method = method
        if '_' in action:
            action = action.replace('_', '-')
        self.action = action

    def __getattr__(self, name):
        self.action = self.action + '/' + name
        return self

    def __call__(self, *args, **kwargs):
        url = self.endpoint + '/' + self.action
        # encode additional kwargs
        if len(kwargs) > 0:
            url += f'?{urllib.parse.urlencode(self.kwargs)}'

        if self.bearer:
            headers = {
                "Authorization": f"Bearer {self.bearer}",
                "Content-Type": "application/json"
            }
        else:
            headers = {}

        if 'data' in kwargs:
            data = kwargs['data']
        if self.method == 'get':
            r = requests.get(url, params=kwargs, headers=headers)
        if self.method == 'post':
            r = requests.post(url, json=data, headers=headers)
        else:
            assert 'not implemented'
        try:
            ret = r.json()
        except JSONDecodeError as e:
            ret = r.text
        return ret

class _API:
    def __init__(self, api, method):
        self.api = api
        self.method = method

    def __getattr__(self, name):
        if self.method == 'get':
            action = Action(self.api, self.method, name)
            return action
        elif self.method == 'post':
            action = Action(self.api, self.method, name)
            return action
        else:
            assert 'not implemented'

class API:
    def __init__(self, endpoint, bearer=None, **kwargs):
        self.endpoint = endpoint
        self.bearer = bearer
        self.kwargs = kwargs

    def __getattr__(self, name):
        _api = _API(self, name)
        return _api


def test_ifconfig_io():
    api = API('https://ifconfig.io')
    ret = api.get.ip()
    # ipv4 regex match
    pattern = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'
    assert re.match(pattern, ret)