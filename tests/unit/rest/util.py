#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilitiy functions to be assigned as methods of asynctest.TestCase.
"""

from unittest import mock
from urllib.parse import parse_qs, urlparse

from asynctest import CoroutineMock, TestCase, patch

class MockRequest(CoroutineMock):

    def __init__(self, name):
        super().__init__(name)
        self.side_effect = self.update
        
    def update(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        (self.scheme, self.netloc, self.path, self.params,  self.query_str, 
         self.fragment) = urlparse(args[0])
        self.url = '{}://{}{}'.format(self.scheme, self.netloc, self.path)
        self.query = parse_qs(self.query_str)
        return mock.DEFAULT


class MockTestCase(TestCase):
    
    def setUp(self):
        mock_get_patcher = patch('aiohttp.ClientSession.get', new_callable=MockRequest)
        self.mock_get = mock_get_patcher.start()
        self.addCleanup(mock_get_patcher.stop)
        
        mock_post_patcher = patch('aiohttp.ClientSession.post', new_callable=MockRequest)
        self.mock_post = mock_post_patcher.start()
        self.addCleanup(mock_post_patcher.stop)
        
        
    def check_mock_req_args(self, mock_req, expected_args, expected_kwargs):
        self.assertEqual(len(mock_req.args), len(expected_args))
        for i, arg_type in enumerate(expected_args):
            self.assertIsInstance(mock_req.args[i], arg_type)
        

    def check_mock_req_url(self, mock_req, expected_url, expected_query=None):
        self.assertEqual(mock_req.url, expected_url)
        
        self.assertEqual(len(mock_req.query), len(expected_query))
        for expected_key, expected_val in expected_query.items():
            self.assertIn(expected_key, mock_req.query)
            self.assertEqual(mock_req.query[expected_key][0], expected_val)
       
    
    def check_mock_req_headers(self, mock_req, expected_headers):
        self.assertEqual(len(mock_req.kwargs['headers']), len(expected_headers))
        for expected_key, expected_val in expected_headers.items():
            self.assertIn(expected_key, mock_req.kwargs['headers'])
            if not expected_val == '*':
                self.assertEqual(mock_req.kwargs['headers'][expected_key], expected_val)
                
                
    def check_mock_req_data(self, mock_req, expected_data):
        self.assertEqual(len(mock_req.kwargs['data']), len(expected_data))
        for expected_key, expected_val in expected_data.items():
            self.assertIn(expected_key, mock_req.kwargs['data'])