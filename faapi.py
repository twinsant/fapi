import urllib
from json import JSONDecodeError
from pprint import pprint

import requests

class Action:
    def __init__(self, api, method, action):
        self.endpoint = api.endpoint
        self.bearer = api.bearer
        self.basic = api.basic
        self.kwargs = api.kwargs
        self.method = method
        if 'logger' in api.kwargs:
            self.logger = api.kwargs['logger']
        if '_' in action:
            action = action.replace('_', '-')
        self.action = action

    def __getattr__(self, name):
        if name in ['logger']:
            return None
        self.action = self.action + '/' + name
        return self

    def __call__(self, *args, **kwargs):
        convert_dash = kwargs.get('convert_dash', False)
        if convert_dash and '-' in self.action:
            self.action = self.action.replace('-', '.')
        url = self.endpoint + '/' + self.action
        if self.logger:
            self.logger.debug(f'URL: {url}')
        # encode additional kwargs
        if len(kwargs) > 0:
            url += f'?{urllib.parse.urlencode(self.kwargs)}'

        if self.bearer:
            headers = {
                "Authorization": f"Bearer {self.bearer}",
                "Content-Type": "application/json"
            }
        elif self.basic:
            headers = {
                "Authorization": f"Basic {self.basic}",
                "Content-Type": "application/json"
            }
        else:
            headers = {}

        self.logger.debug(f'HEADERS: {headers}')

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
    def __init__(self, endpoint, bearer=None, basic=None, **kwargs):
        self.endpoint = endpoint
        self.bearer = bearer
        self.basic = basic
        self.kwargs = kwargs

    def __getattr__(self, name):
        _api = _API(self, name)
        return _api

if __name__ == '__main__':
    api = API('https://ifconfig.io')
    pprint(api.get.foo_dash())
    pprint(api.get.all_json(convert_dash=True))