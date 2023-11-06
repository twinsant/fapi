import urllib
from json import JSONDecodeError
import re
from pprint import pprint

import pytest
import requests
from loguru import logger

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
        if '-' in self.action:
            self.action = self.action.replace('-', '.')
        url = self.endpoint + '/' + self.action
        logger.debug(f'URL: {url}')
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

class Ifconfg:
    def __init__(self):
        self.api = API('https://ifconfig.io')

@pytest.fixture
def _api():
    return Ifconfg()

def is_ipv4_or_ipv6(text):
    # ipv4 regex match
    ipv4_pattern = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'
    ipv6_pattern = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
    return re.match(ipv4_pattern, text) or re.match(ipv6_pattern, text)

def test_ifconfig_io(_api):
    ret = _api.api.get.ip()
    assert is_ipv4_or_ipv6(ret)

def test_ifconfig_io_ua(_api):
    ret = _api.api.get.ua()
    assert ret == 'python-requests/2.31.0\n'

def test_ifconfig_io_lang(_api):
    ret = _api.api.get.lang()
    assert ret == '\n'

def test_ifconfig_io_forwarded(_api):
    ret = _api.api.get.forwarded()
    assert is_ipv4_or_ipv6(ret)

def test_ifconfig_io_all_json(_api):
    ret = _api.api.get.all_json()
    assert is_ipv4_or_ipv6(ret['ip'])

def test_ifconfig_io_404(_api):
    ret = _api.api.get.foo()
    assert ret == '404 page not found'

if __name__ == '__main__':
    api = API('https://ifconfig.io')
    pprint(api.get.all_json())