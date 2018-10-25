#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.rest.Client` class.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
import time

from asynctest import TestCase

from copra.rest import Client, SANDBOX_URL

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PASSPHRASE = os.getenv('PASSPHRASE')
TEST_AUTH = True if (KEY and SECRET and PASSPHRASE) else False

class TestRest(TestCase):
    """Tests for copra.rest.Client"""
    
    def setUp(self):
        self.client = Client(self.loop)
        self.auth_client = Client(self.loop, auth=True, key=KEY, secret=SECRET, 
                                  passphrase=PASSPHRASE)
                                  
    def tearDown(self):
        self.loop.create_task(self.client.close())
        self.loop.create_task(self.auth_client.close())
        self.loop.run_until_complete(asyncio.sleep(0.250))

    async def test_get_products(self):
        
        keys = ('id', 'base_currency', 'quote_currency', 'base_min_size', 
                'base_max_size', 'quote_increment', 'display_name', 'status',
                'margin_enabled', 'status_message', 'min_market_funds', 
                'max_market_funds', 'post_only', 'limit_only', 'cancel_only')
        
        # Sometimes returns 'accesible' as a key. ?? 
        
        products = await self.client.get_products()

        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 1)
        self.assertIsInstance(products[0], dict)
        self.assertGreaterEqual(len(products[0]), len(keys))
        for key in keys:
            self.assertIn(key, products[0])
            
            
    async def test_order_book(self):
        
        keys = ('sequence', 'bids', 'asks')
        
        ob1 = await self.client.get_order_book('BTC-USD', level=1)
        self.assertIsInstance(ob1, dict)
        self.assertEqual(len(ob1), len(keys))
        for key in keys:
            self.assertIn(key, ob1)
        self.assertIsInstance(ob1['bids'], list)
        self.assertEqual(len(ob1['bids']), 1)
        self.assertEqual(len(ob1['bids'][0]), 3)
        self.assertIsInstance(ob1['asks'], list)
        self.assertEqual(len(ob1['asks']), 1)
        self.assertEqual(len(ob1['asks'][0]), 3)
        
        ob2 = await self.client.get_order_book('BTC-USD', level=2)
        self.assertIsInstance(ob2, dict)
        self.assertEqual(len(ob2), len(keys))
        for key in keys:
            self.assertIn(key, ob2)
        self.assertIsInstance(ob2['bids'], list)
        self.assertEqual(len(ob2['bids']), 50)
        self.assertEqual(len(ob2['bids'][0]), 3)
        self.assertIsInstance(ob2['asks'], list)
        self.assertEqual(len(ob2['asks']), 50)
        self.assertEqual(len(ob2['asks'][0]), 3)
                
        
        ob3 = await self.client.get_order_book('BTC-USD', level=2)
        self.assertIsInstance(ob3, dict)
        self.assertEqual(len(ob3), len(keys))
        for key in keys:
            self.assertIn(key, ob3)
        self.assertIsInstance(ob3['bids'], list)
        self.assertEqual(len(ob3['bids']), 50)
        self.assertEqual(len(ob3['bids'][0]), 3)
        self.assertIsInstance(ob3['asks'], list)
        self.assertGreaterEqual(len(ob3['asks']), 50)
        self.assertGreaterEqual(len(ob3['asks'][0]), 3)            

            

            
    #             ob3 = await client.get_order_book('BTC-USD', level=3)
    #             self.assertIsInstance(ob3, dict)
    #             self.assertEqual(len(ob3), 3)
    #             self.assertIn('sequence', ob3)
    #             self.assertIn('bids', ob3)
    #             self.assertIn('asks', ob3)
    #             self.assertGreater(len(ob3['bids']), 50)
    #             self.assertGreater(len(ob3['asks']), 50)