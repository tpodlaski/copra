#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.BaseClient` class.
"""

import asyncio

import aiohttp

from copra.rest import BaseClient, HEADERS
from tests.unit.rest.util import MockTestCase

        
class TestBaseClient(MockTestCase):
    """Tests for copra.rest.BaseClient"""
    
    async def test___init__(self):
        client = BaseClient(self.loop)
        self.assertEqual(client.loop, self.loop)
        self.assertIsInstance(client.session, aiohttp.ClientSession)
        self.assertFalse(client.session.closed)
        await client.session.close()
        self.assertTrue(client.session.closed)

        
    async def test_close(self):
        client = BaseClient(self.loop)
        self.assertFalse(client.session.closed)
        self.assertFalse(client.closed)
        await client.close()
        self.assertTrue(client.session.closed)
        self.assertTrue(client.closed)

        
    async def test_context_manager(self):
        async with BaseClient(self.loop) as client:
            self.assertFalse(client.closed)
        self.assertTrue(client.closed)
    
        try:
            async with BaseClient(self.loop) as client:
                raise ValueError()
        except ValueError:
            pass
        self.assertTrue(client.closed)
        
    
    async def test_get(self):
        
        #url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.get()
        
        url = 'http://httpbin.org/'
        params = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        #No params, default headers
        resp = await client.get(url)
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, {})
        self.check_mock_req_headers(self.mock_get, HEADERS)
        
        #Params, default headers
        resp = await client.get(url, params)
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, params)
        self.check_mock_req_headers(self.mock_get, HEADERS)
        
        #Params, no headers
        resp = await client.get(url, params, headers={})
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, params)
        self.check_mock_req_headers(self.mock_get, {})
        
        #Params, non-default headers
        resp = await client.get(url, params, headers=headers)
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, params)
        self.check_mock_req_headers(self.mock_get, headers)
        
        
        
