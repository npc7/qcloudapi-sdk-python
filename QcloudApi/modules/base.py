#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
import time
import random
import sys
import os
import warnings
warnings.filterwarnings("ignore")

from ..common.request import ApiRequest, RequestInternal
from ..common.sign import Sign
from ..common.api_exception import ApiServerNetworkException, ApiClientParamException
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

class Base:
    requestHost = ''
    requestUri = '/v2/index.php'
    _params = {}
    version = 'SDK_PYTHON_2.0'

    def __init__(self, config):
        self.secretId = config['secretId']
        self.secretKey = config['secretKey']
        self.defaultRegion = config.get('Region','')
        self.Version = config.get('Version','')
        self.method = config.get('method','GET').upper()
        self.sign_method = config.get('SignatureMethod','HmacSHA1')
        self.apiRequest = ApiRequest(self.requestHost)
        self.Token = config.get('Token','')

    def set_req_timeout(self, req_timeout):
        self.apiRequest.set_req_timeout(req_timeout)

    def open_debug(self):
        self.apiRequest.set_debug(True)

    def close_debug(self):
        self.apiRequest.set_debug(False)

    def _build_header(self, req_inter):
        if self.apiRequest.is_keep_alive():
            req_inter.header["Connection"] = "Keep-Alive"
        if req_inter.method == 'POST':
            req_inter.header["Content-Type"] = "application/x-www-form-urlencoded"

    def _fix_params(self, params):
        if not isinstance(params, (dict,)):
            return params
        return self._format_params(None, params)

    def _format_params(self, prefix, params):
        d = {}
        if params is None:
            return d

        if not isinstance(params, (tuple, list, dict)):
            d[prefix] = params
            return d

        if isinstance(params, (list, tuple)):
            for idx, item in enumerate(params):
                if prefix:
                    key = "{0}.{1}".format(prefix, idx)
                else:
                    key = "{0}".format(idx)
                d.update(self._format_params(key, item))
            return d

        if isinstance(params, dict):
            for k, v in params.items():
                if prefix:
                    key = '{0}.{1}'.format(prefix, k)
                else:
                    key = '{0}'.format(k)
                d.update(self._format_params(key, v))
            return d

        raise ApiClientParamException('some params type error')

    def _build_req_inter(self, action, params, req_inter):
        _params = copy.deepcopy(self._fix_params(params))
        _params['Action'] = action[0].upper() + action[1:]
        _params['RequestClient'] = self.version

        if ('Region' not in _params and self.defaultRegion!=''):
            _params['Region'] = self.defaultRegion

        if ('Version' not in _params and self.Version!=''):
            _params['Version'] = self.Version

        if ('Token' not in _params and self.Token!=''):
            _params['Token'] = self.Token

        if ('SecretId' not in _params):
            _params['SecretId'] = self.secretId

        if ('Nonce' not in _params):
            _params['Nonce'] = random.randint(1, sys.maxsize)

        if ('Timestamp' not in _params):
            _params['Timestamp'] = int(time.time())

        if ('SignatureMethod' in _params):
            self.sign_method = _params['SignatureMethod']
        else:
            _params['SignatureMethod'] = self.sign_method

        sign = Sign(self.secretId, self.secretKey)
        _params['Signature'] = sign.make(req_inter.host, req_inter.uri, _params, req_inter.method, self.sign_method)

        req_inter.data = urlencode(_params)

        self._build_header(req_inter)

    def _check_status(self, resp_inter):
        if resp_inter.status != 200:
            raise ApiServerNetworkException(resp_inter.status, resp_inter.header, resp_inter.data)

    def generateUrl(self, action, params):
        req_inter = RequestInternal(self.requestHost, self.method, self.requestUri)
        self._build_req_inter(action, params, req_inter)
        url = 'https://%s%s' % (req_inter.host, req_inter.uri)
        if (req_inter.method == 'GET'):
            url += '?' + req_inter.data
        return url

    def call(self, action, params, files = {}):
        req_inter = RequestInternal(self.requestHost, self.method, self.requestUri)
        self._build_req_inter(action, params, req_inter)
        resp_inter = self.apiRequest.send_request(req_inter)
        self._check_status(resp_inter)
        return resp_inter.data

def main():
    action = 'DescribeInstances'
    config = {
        'Region': 'gz',
        'secretId': '你的secretId',
        'secretKey': '你的secretKey',
        'method': 'get',
    }
    params = {}
    base = Base(config)
    print((base.call(action, params)))

if (__name__ == '__main__'):
    main()