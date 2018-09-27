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
        
    def test_context_manager(self):
        async def go():
            async with Client(self.loop) as client:
                self.assertFalse(client.session.closed)
            self.assertTrue(client.session.closed)
            
            try:
                async with Client(self.loop) as client:
                    self.assertFalse(client.session.closed)
                    #Throws ValueError
                    ob = await client.get_product_order_book('BTC-USD', level=99)
            except ValueError as e:
                pass
            self.assertTrue(client.session.closed)
            
        self.loop.run_until_complete(go())
        
    # def test_get(self):
    #     async def go():
    #         async with Client(self.loop, 'http://httpbin.org/') as client:
    #             params = {'key1': 'item1', 'key2': 'item2'}
    #             resp = await client.get('/get', params)
    #             self.assertIsInstance(resp, dict)
    #             self.assertEqual(len(resp['args']), 2)
    #             self.assertEqual(resp['args']['key1'], 'item1')
    #             self.assertEqual(resp['args']['key2'], 'item2')
    #             self.assertEqual(resp['url'], 'http://httpbin.org/get?key1=item1&key2=item2')

    #         async with Client(self.loop, 'http://httpbin.org/') as client:
    #             resp = await client.get('/get', raw=True)
    #             self.assertIsInstance(resp, aiohttp.client_reqrep.ClientResponse)

    #     self.loop.run_until_complete(go())
        
    # def test_get_products(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             products = await client.get_products()
    #             self.assertIsInstance(products, list)
    #             self.assertIsInstance(products[0], dict)
    #             self.assertGreater(len(products), 1)
    #             self.assertIn('base_currency', products[0])
    #             self.assertIn('quote_currency', products[0])

    #     self.loop.run_until_complete(go())
            
    def test_get_product_order_book(self):
        async def go():
            async with Client(self.loop) as client:
            
                with self.assertRaises(ValueError):
                    ob = await client.get_product_order_book('BTC-USD', 99)
                
                ob1 = await client.get_product_order_book('BTC-USD')
                self.assertIsInstance(ob1, dict)
                self.assertEqual(len(ob1), 3)
                self.assertIn('sequence', ob1)
                self.assertIn('bids', ob1)
                self.assertIn('asks', ob1)
                self.assertEqual(len(ob1['bids']), 1)
                self.assertEqual(len(ob1['asks']), 1)
            
                ob1 = await client.get_product_order_book('BTC-USD', level=1)
                self.assertIsInstance(ob1, dict)
                self.assertEqual(len(ob1), 3)
                self.assertIn('sequence', ob1)
                self.assertIn('bids', ob1)
                self.assertIn('asks', ob1)
                self.assertEqual(len(ob1['bids']), 1)
                self.assertEqual(len(ob1['asks']), 1)
            
                ob2 = await client.get_product_order_book('BTC-USD', level=2)
                self.assertIsInstance(ob2, dict)
                self.assertEqual(len(ob2), 3)
                self.assertIn('sequence', ob2)
                self.assertIn('bids', ob2)
                self.assertIn('asks', ob2)
                self.assertEqual(len(ob2['bids']), 50)
                self.assertEqual(len(ob2['asks']), 50)
            
                ob3 = await client.get_product_order_book('BTC-USD', level=3)
                self.assertIsInstance(ob3, dict)
                self.assertEqual(len(ob3), 3)
                self.assertIn('sequence', ob3)
                self.assertIn('bids', ob3)
                self.assertIn('asks', ob3)
                self.assertGreater(len(ob3['bids']), 50)
                self.assertGreater(len(ob3['asks']), 50)
            
        self.loop.run_until_complete(go())
            
            