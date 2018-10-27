#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilitiy functions to be assigned as methods of asynctest.TestCase.
"""

from unittest import mock
from urllib.parse import parse_qs, urlparse

from asynctest import CoroutineMock


def update_mock_req(mock_req, *args, **kwargs):
    mock_req.args = args
    mock_req.kwargs = kwargs
    (mock_req.scheme, mock_req.netloc, mock_req.path, mock_req.params, 
     mock_req.query_str, mock_req.fragment) = urlparse(args[0])
    mock_req.query = parse_qs(mock_req.query_str)
    return mock.DEFAULT


def update_mock_get(self, *args, **kwargs):
    return update_mock_req(self.mock_get, *args, **kwargs)


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