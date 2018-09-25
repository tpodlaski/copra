#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `copra.rest` module.

Uses http://httpbin.org/ - HTTP Request & Response Service
"""

import asyncio
import unittest

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