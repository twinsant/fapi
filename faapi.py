import urllib
from json import JSONDecodeError
from pprint import pprint

import requests
from requests.auth import HTTPBasicAuth

class Action:
    def __init__(self, api, method, action, convert_to_dash=True):
        self.endpoint = api.endpoint
        self.bearer = api.bearer
        self.basic = api.basic
        self.method = method

        if 'logger' in api.kwargs:
            self.logger = api.kwargs['logger']
            del api.kwargs['logger']
        self.kwargs = api.kwargs

        if '_' in action and convert_to_dash:
            action = action.replace('_', '-')
        self.action = action

        if 'param' in api.kwargs:
            self.param = api.kwargs['param']
        else:
            self.param = None

    def __getattr__(self, name):
        if name in ['logger']:
            return None
        self.action = self.action + '/' + name
        return self

    def __call__(self, *args, **kwargs):
        '''
        data=<post or get data>
        '''
        # Call parameters here
        underline2dot = kwargs.get('underline2dot', False)
        convert_dash = kwargs.get('convert_dash', False)
        proxies = kwargs.get('proxies', None)
        if underline2dot and '-' in self.action:
            self.action = self.action.replace('-', '.')
        elif convert_dash and '-' in self.action:
            self.action = self.action.replace('-', '.')
        url = self.endpoint + '/' + self.action
        if self.param:
            url = url + '/' + self.param

        # NOTE: encode additional kwargs
        if len(kwargs) > 0:
            url += f'?{urllib.parse.urlencode(self.kwargs)}'

        if self.logger:
            self.logger.debug(f'URL: {url}')

        if self.bearer:
            headers = {
                "Authorization": f"Bearer {self.bearer}",
                "Content-Type": "application/json"
            }
        elif 'headers' in kwargs:
            headers = kwargs['headers']
        else:
            headers = {}

        if self.logger:
            self.logger.debug(f'HEADERS: {headers}')
            self.logger.debug(self.method)

        if 'data' in kwargs:
            data = kwargs['data']
        else:
            data = None
        if self.logger:
            self.logger.debug(f'DATA: {data}')
        if self.method == 'get':
            r = requests.get(url, params=data, headers=headers, proxies=proxies)
        if self.method == 'post':
            r = requests.post(url, json=data, headers=headers, proxies=proxies)
        if self.method == 'put':
            r = requests.put(url, params=data, headers=headers, proxies=proxies)
        if self.method == 'post_form':
            if self.basic:
                basic = HTTPBasicAuth(*self.basic.split(':'))
                r = requests.post(url, data=data, headers=headers, auth=basic)
            else:
                r = requests.post(url, data=data, headers=headers)
        else:
            assert 'not implemented'
        try:
            ret = r.json()
        except JSONDecodeError as e:
            ret = r.text
        return ret

class _API:
    def __init__(self, api, method, **kwargs):
        self.api = api
        self.method = method
        if 'convert_to_dash' in kwargs:
            self.convert_to_dash = kwargs['convert_to_dash']
        else:
            self.convert_to_dash = True

    def __getattr__(self, name):
        if self.method == 'get':
            action = Action(self.api, self.method, name, convert_to_dash=self.convert_to_dash)
            return action
        elif self.method == 'post':
            action = Action(self.api, self.method, name, convert_to_dash=self.convert_to_dash)
            return action
        elif self.method == 'put':
            action = Action(self.api, self.method, name, convert_to_dash=self.convert_to_dash)
            return action
        elif self.method == 'post_form':
            action = Action(self.api, self.method, name, convert_to_dash=self.convert_to_dash)
            return action
        else:
            assert 'not implemented'

class API:
    '''
    param will put {param} in url path
    '''
    def __init__(self, endpoint, bearer=None, basic=None, **kwargs):
        self.endpoint = endpoint
        self.bearer = bearer
        self.basic = basic
        self.kwargs = kwargs

    def __getattr__(self, name):
        _api = _API(self, name, **self.kwargs)
        return _api

if __name__ == '__main__':
    api = API('https://ifconfig.io')
    pprint(api.get.foo_dash())
    pprint(api.get.all_json(convert_dash=True))