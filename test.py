import pytest

import os
import sys
import re
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from faapi import API

class Ifconfg:
    def __init__(self):
        self.api = API('https://ifconfig.io')

@pytest.fixture
def _cfg():
    return Ifconfg()

def is_ipv4_or_ipv6(text):
    # ipv4 regex match
    ipv4_pattern = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'
    ipv6_pattern = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
    return re.match(ipv4_pattern, text) or re.match(ipv6_pattern, text)

def test_ifconfig_io(_cfg):
    ret = _cfg.api.get.ip()
    assert is_ipv4_or_ipv6(ret)

def test_ifconfig_io_ua(_cfg):
    ret = _cfg.api.get.ua()
    assert ret == 'python-requests/2.28.2\n'

def test_ifconfig_io_lang(_cfg):
    ret = _cfg.api.get.lang()
    assert ret == '\n'

def test_ifconfig_io_forwarded(_cfg):
    ret = _cfg.api.get.forwarded()
    assert is_ipv4_or_ipv6(ret)

def test_ifconfig_io_all_json(_cfg):
    ret = _cfg.api.get.all_json(convert_dash=True)
    assert ret['ifconfig_hostname'] == 'ifconfig.io'

def test_ifconfig_io_404(_cfg):
    ret = _cfg.api.get.foo()
    assert ret == '404 page not found'

def test_all_json(_cfg):
    ret = _cfg.api.get.all_json(underline2dot=True)
    print(ret)
    assert ret['ifconfig_hostname'] == 'ifconfig.io'