#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.rest.Client` class.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import os

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
        
    async def test_get_products(self):
        
        keys = ('id', 'base_currency', 'quote_currency', 'base_min_size', 
                'base_max_size', 'quote_increment', 'display_name', 'status',
                'margin_enabled', 'status_message', 'min_market_funds', 
                'max_market_funds', 'post_only', 'limit_only', 'cancel_only')
        
        products = await self.client.get_products()
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 1)
        self.assertIsInstance(products[0], dict)
        self.assertEqual(len(products[0]), len(keys))
        for key in keys:
            self.assertIn(key, products[0])
