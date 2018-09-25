#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `copra.rest` module.

Uses http://httpbin.org/ - HTTP Request & Response Service
"""

import asyncio
import unittest

import aiohttp

from copra.rest import Client

class TestClient(unittest.TestCase):
    """Tests for copra.rest.client"""
    
    def setUp(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()
    
    def test__init__(self):
        async def go():
            client = Client(self.loop)
            self.assertEqual(client.url, 'https://api.pro.coinbase.com')
            await client.close()
            
            client = Client(self.loop, 'http://httpbin.org/')
            self.assertEqual(client.url, 'http://httpbin.org/')
            await client.close()
        
        self.loop.run_until_complete(go())
        
    def test_close(self):
        async def go():
            client = Client(self.loop)
            self.assertFalse(client.session.closed)
            
            await client.close()
            self.assertTrue(client.session.closed)
            
        self.loop.run_until_complete(go())
        
    def test_get(self):
        async def go():
            client = Client(self.loop, 'http://httpbin.org/')
            params = {'key1': 'item1', 'key2': 'item2'}
            resp = await client.get('/get', params)
            self.assertIsInstance(resp, dict)
            self.assertEqual(len(resp['args']), 2)
            self.assertEqual(resp['args']['key1'], 'item1')
            self.assertEqual(resp['args']['key2'], 'item2')
            self.assertEqual(resp['url'], 'http://httpbin.org/get?key1=item1&key2=item2')
            await client.close()
            
            client = Client(self.loop, 'http://httpbin.org/')
            resp = await client.get('/get', raw=True)
            self.assertIsInstance(resp, aiohttp.client_reqrep.ClientResponse)
            await client.close()
            
        self.loop.run_until_complete(go())
        
    
            