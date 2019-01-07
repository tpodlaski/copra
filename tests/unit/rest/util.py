#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilitiy functions to be assigned as methods of asynctest.TestCase.
"""

import json
import functools
from unittest import mock
from urllib.parse import parse_qsl, urlparse

from multidict import MultiDict

from asynctest import CoroutineMock, TestCase, patch

class MockRequest(CoroutineMock):

    def __init__(self, name):
        super().__init__(name)
        self.side_effect = self.update
 
        
    def update(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.headers = self.kwargs['headers']
        (self.scheme, self.netloc, self.path, self.params,  self.query_str, 
         self.fragment) = urlparse(args[0])
        self.url = '{}://{}{}'.format(self.scheme, self.netloc, self.path)
        self.query = MultiDict(parse_qsl(self.query_str))
        if 'data' in self.kwargs:
            self.data = json.loads(self.kwargs['data']) if self.kwargs['data'] else {}
        else:
            self.data = {}
        return mock.DEFAULT


class MockTestCase(TestCase):
    
    def setUp(self):
        mock_get_patcher = patch('aiohttp.ClientSession.get', new_callable=MockRequest)
        self.mock_get = mock_get_patcher.start()
        self.mock_get.method = 'GET'
        self.mock_get.return_value.json = CoroutineMock()
        self.mock_get.return_value.status = 200
        self.addCleanup(mock_get_patcher.stop)
        
        mock_post_patcher = patch('aiohttp.ClientSession.post', new_callable=MockRequest)
        self.mock_post = mock_post_patcher.start()
        self.mock_post.method = 'POST'
        self.mock_post.return_value.json = CoroutineMock()
        self.mock_post.return_value.status = 200
        self.addCleanup(mock_post_patcher.stop)
        
        mock_del_patcher = patch('aiohttp.ClientSession.delete', new_callable=MockRequest)
        
        self.mock_del = mock_del_patcher.start()
        self.mock_del.method = 'DEL'
        self.mock_del.return_value.json = CoroutineMock()
        self.mock_del.return_value.status = 200
        self.addCleanup(mock_del_patcher.stop)

    
    def check_req(self, mock_req, url='', query=None, data=None, headers=None):
        if not query:
            query = {}
        if not data:
            data = {}
        if not headers:
            headers = {}
        if mock_req.method == 'GET':
            query['no-cache'] = mock_req.query['no-cache']
        self.assertEqual(mock_req.url, url)
        self.assertEqual(mock_req.query.items(), MultiDict(query).items())
        
        self.assertEqual(len(mock_req.headers), len(headers))
        for key, val in headers.items():
            self.assertIn(key, mock_req.headers)
            if not val == '*':
                self.assertEqual(mock_req.headers[key], val)
                
        self.assertEqual(mock_req.data, data)