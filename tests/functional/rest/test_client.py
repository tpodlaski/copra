#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.rest.Client` class.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from datetime import datetime, timedelta
import os
import json
import time

from asynctest import TestCase, skipUnless, expectedFailure

from copra.rest import Client, SANDBOX_URL, USER_AGENT

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PASSPHRASE = os.getenv('PASSPHRASE')
TEST_AUTH = True if (KEY and SECRET and PASSPHRASE) else False
TEST_ACCOUNT = os.getenv('TEST_ACCOUNT')

HTTPBIN = 'http://httpbin.org'

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
        #try to avoid public rate limit
        self.loop.run_until_complete(asyncio.sleep(0.5))


    async def test_delete(self):
        async with Client(self.loop, HTTPBIN) as client:
            headers, body = await client.delete('/delete')
            self.assertEqual(body['args'], {})
            self.assertEqual(body['headers']['User-Agent'], USER_AGENT)
            self.assertIsInstance(headers, dict)
            self.assertIn('Content-Type', headers)
            self.assertIn('Content-Length', headers)
            
            params = {'key1': 'item1', 'key2': 'item2'}
            headers, body = await client.delete('/delete', params=params)
            self.assertEqual(body['args'], params)
            

    async def test_get(self):
        async with Client(self.loop, HTTPBIN) as client:
            headers, body = await client.get('/get')
            self.assertEqual(body['args'], {})
            self.assertEqual(body['headers']['User-Agent'], USER_AGENT)
            self.assertIsInstance(headers, dict)
            self.assertIn('Content-Type', headers)
            self.assertIn('Content-Length', headers)
            
            params = {'key1': 'item1', 'key2': 'item2'}
            headers, body = await client.get('/get', params=params)
            self.assertEqual(body['args'], params)
            
            
    async def test_post(self):
        async with Client(self.loop, HTTPBIN) as client:
            headers, body = await client.post('/post')
            self.assertEqual(body['form'], {})
            self.assertEqual(body['headers']['User-Agent'], USER_AGENT)
            self.assertIsInstance(headers, dict)
            self.assertIn('Content-Type', headers)
            self.assertIn('Content-Length', headers)
            
            data = {"key1": "item1", "key2": "item2"}
            headers, body = await client.post('/post', data=data)
            self.assertEqual(json.loads(body['data']), data)
        
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

    
    async def test_get_ticker(self):
        
        keys = ('trade_id', 'price', 'size', 'bid', 'ask', 'volume', 'time')
        
        tick = await self.client.get_ticker('BTC-USD')
        self.assertIsInstance(tick, dict)
        self.assertEqual(len(tick), len(keys))
        for key in keys:
            self.assertIn(key, tick)
        
    
    async def test_get_trades(self):
        
        keys = ('time', 'trade_id', 'price', 'size', 'side')
        
        trades, before, after = await self.client.get_trades('BTC-USD')
        self.assertIsInstance(trades, list)
        self.assertIsInstance(trades[0], dict)
        self.assertIsInstance(before, str)
        self.assertIsInstance(after, str)
        self.assertEqual(len(trades), 100)
        for key in keys:
            self.assertIn(key, trades[0])
            
        trades, before, after = await self.client.get_trades('BTC-USD', 5)
        self.assertEqual(len(trades), 5)

        trades_after, after_after, before_after = await self.client.get_trades('BTC-USD', 5, after=after)
        self.assertLess(trades_after[0]['trade_id'], trades[-1]['trade_id'])
                
        trades_before, after_before, before_before = await self.client.get_trades('BTC-USD', 5, before=before)
        if trades_before:
            self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
        else:
            self.assertIsNone(after_before)
            self.assertIsInstance(after_after, str)
            
            await asyncio.sleep(20)
    
            trades_before, after_before, before_before = await self.client.get_trades('BTC-USD', 5, before=before)
            if (trades_before):
                self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
            else:
                self.assertIsNone(after_before)
                self.assertIsInstance(after_after, str)

             
    async def test_get_historic_rates(self):
        
        rates = await self.client.get_historic_rates('BTC-USD', 900)
        self.assertIsInstance(rates, list)
        self.assertEqual(len(rates[0]), 6)
        self.assertEqual(rates[0][0] - rates[1][0], 900)
                
        stop = datetime.utcnow()
        start = stop - timedelta(days=1)
        rates = await self.client.get_historic_rates('LTC-USD', 3600, start.isoformat(), stop.isoformat())
        self.assertIsInstance(rates, list)
        self.assertEqual(len(rates), 24)
        self.assertEqual(len(rates[0]), 6)
        self.assertEqual(rates[0][0] - rates[1][0], 3600)
 
        
    async def test_get_24hour_stats(self):
        
        keys = ('open', 'high', 'low', 'volume', 'last', 'volume_30day')
        
        stats = await self.client.get_24hour_stats('BTC-USD')
        self.assertIsInstance(stats, dict)
        self.assertEqual(len(stats), len(keys))
        for key in keys:
            self.assertIn(key, stats)
       
       
    async def test_get_currencies(self):
        
        keys = ('id', 'name', 'min_size', 'status', 'message')
        
        currencies = await self.client.get_currencies()
        self.assertIsInstance(currencies, list)
        self.assertGreater(len(currencies), 1)
        self.assertIsInstance(currencies[0], dict)
        self.assertEqual(len(currencies[0]), len(keys))
        for key in keys:
            self.assertIn(key, currencies[0])
    
    
    async def test_get_server_time(self):
        
        time = await self.client.get_server_time()
        self.assertIsInstance(time, dict)
        self.assertIn('iso', time)
        self.assertIn('epoch', time)
        self.assertIsInstance(time['iso'], str)
        self.assertIsInstance(time['epoch'], float)
        
        
    @skipUnless(TEST_AUTH, "Authentication credentials not provided.")
    async def test_list_accounts(self):
        
        keys = ('id', 'currency', 'balance', 'available', 'hold', 'profile_id')
        
        accounts = await self.auth_client.list_accounts()
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], dict)
        for key in keys:
            self.assertIn(key, accounts[0])
        

    @skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    async def test_get_account(self):
        
        keys = ('id', 'currency', 'balance', 'available', 'hold', 'profile_id')
        
        account = await self.auth_client.get_account(TEST_ACCOUNT)
        self.assertIsInstance(account, dict)
        for key in keys:
            self.assertIn(key, account)
            
            
    # TO DO
    @expectedFailure
    @skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    async def test_get_account_history(self):
        assert False
        
    # TO DO   
    @expectedFailure
    @skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    async def test_get_holds(self):
        assert False
        
        
    # TO DO   
    @expectedFailure
    @skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    async def test_place_order(self):
        assert False
        