#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.BaseClient` class.
"""

import asyncio

import aiohttp
from asynctest import CoroutineMock, patch, TestCase

from copra.rest import BaseClient, HEADERS
from tests.unit.rest.util import *

        
class TestBaseClient(TestCase):
    """Tests for copra.rest.BaseClient"""
    
    update_mock_get = update_mock_get
    check_mock_get_args = check_mock_get_args
    check_mock_get_url = check_mock_get_url
    check_mock_get_headers = check_mock_get_headers
        
    def setUp(self):
        mock_get_patcher = patch('aiohttp.ClientSession.get', new_callable=CoroutineMock)
        self.mock_get = mock_get_patcher.start()
        self.mock_get.side_effect = self.update_mock_get
        self.addCleanup(mock_get_patcher.stop)
        
    
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
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url(url, {})
        self.check_mock_get_headers(HEADERS)
        
        #Params, default headers
        resp = await client.get(url, params)
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url(url, params)
        self.check_mock_get_headers(HEADERS)
        
        #Params, no headers
        resp = await client.get(url, params, headers={})
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url(url, params)
        self.check_mock_get_headers({})
        
        #Params, non-default headers
        resp = await client.get(url, params, headers=headers)
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url(url, params)
        self.check_mock_get_headers(headers)
        
        
        
