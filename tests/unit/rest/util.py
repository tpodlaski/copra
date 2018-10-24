#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilitiy functions to be assigned as methods of unittest.TestCase.
"""

from unittest import mock
from urllib.parse import parse_qs, urlparse

from asynctest import CoroutineMock

def update_mock_get(self, *args, **kwargs):
    self.mock_get.args = args
    self.mock_get.kwargs = kwargs
    (self.mock_get.scheme, self.mock_get.netloc, 
     self.mock_get.path, self.mock_get.params, self.mock_get.query_str, 
     self.fragment) = urlparse(args[0])
    self.mock_get.query = parse_qs(self.mock_get.query_str)
    return mock.DEFAULT


def check_mock_get_args(self, expected_args, expected_kwargs):
    self.assertEqual(len(self.mock_get.args), len(expected_args))
    for i, arg_type in enumerate(expected_args):
        self.assertIsInstance(self.mock_get.args[i], arg_type)

        
def check_mock_get_url(self, expected_url, expected_query=None):
    self.assertEqual('{}://{}{}'.format(self.mock_get.scheme, 
        self.mock_get.netloc, self.mock_get.path), expected_url)
    
    self.assertEqual(len(self.mock_get.query), len(expected_query))
    for expected_key, expected_val in expected_query.items():
        self.assertIn(expected_key, self.mock_get.query)
        self.assertEqual(self.mock_get.query[expected_key][0], expected_val)

        
def check_mock_get_headers(self, expected_headers):
    self.assertEqual(len(self.mock_get.kwargs['headers']), len(expected_headers))
    for expected_key, expected_val in expected_headers.items():
        self.assertIn(expected_key, self.mock_get.kwargs['headers'])
        if not expected_val == '*':
            self.assertEqual(self.mock_get.kwargs['headers'][expected_key], expected_val)