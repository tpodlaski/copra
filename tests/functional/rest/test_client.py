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
import random
import time
from uuid import uuid4

from asynctest import TestCase, skipUnless, expectedFailure
from dateutil import parser

from copra.rest import APIRequestError, Client, SANDBOX_URL, USER_AGENT

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PASSPHRASE = os.getenv('PASSPHRASE')
TEST_AUTH = True if (KEY and SECRET and PASSPHRASE) else False
TEST_BTC_ACCOUNT = os.getenv('TEST_BTC_ACCOUNT')
TEST_USD_ACCOUNT = os.getenv('TEST_USD_ACCOUNT')
TEST_USD_DEPOSIT_METHOD = os.getenv('TEST_USD_DEPOSIT_METHOD')
TEST_USD_COINBASE_ACCOUNT = os.getenv('TEST_USD_COINBASE_ACCOUNT')

HTTPBIN = 'http://httpbin.org'

class TestRest(TestCase):
    """Tests for copra.rest.Client"""
    
    def setUp(self):
        self.client = Client(self.loop)
        self.auth_client = Client(self.loop, SANDBOX_URL, auth=True, key=KEY, secret=SECRET, 
                                  passphrase=PASSPHRASE)
     
                                  
    def tearDown(self):
        self.loop.run_until_complete(self.auth_client.cancel_all())
        self.loop.create_task(self.client.close())
        self.loop.create_task(self.auth_client.close())
        self.loop.run_until_complete(asyncio.sleep(0.250))
        #try to avoid public rate limit
        self.loop.run_until_complete(asyncio.sleep(0.5))
        
        
    # async def test_user_agent(self):
        
    #     async with Client(self.loop, HTTPBIN) as client:
    #         headers, body = await client.get('/user-agent')
    #         self.assertEqual(body['user-agent'], USER_AGENT)

    
    # async def test_handle_error(self):
    #     async with Client(self.loop, HTTPBIN) as client:
        
    #         with self.assertRaises(APIRequestError) as cm:
    #             headers, body = await client.get('/status/404')
                

    # async def test_delete(self):
    #     async with Client(self.loop, HTTPBIN) as client:
    #         headers, body = await client.delete('/delete')
    #         self.assertEqual(body['args'], {})
    #         self.assertEqual(body['headers']['User-Agent'], USER_AGENT)
    #         self.assertIsInstance(headers, dict)
    #         self.assertIn('Content-Type', headers)
    #         self.assertIn('Content-Length', headers)
            
    #         params = {'key1': 'item1', 'key2': 'item2'}
    #         headers, body = await client.delete('/delete', params=params)
    #         self.assertEqual(body['args'], params)
            

    # async def test_get(self):
    #     async with Client(self.loop, HTTPBIN) as client:
    #         headers, body = await client.get('/get')
    #         self.assertEqual(body['args'], {})
    #         self.assertEqual(body['headers']['User-Agent'], USER_AGENT)
    #         self.assertIsInstance(headers, dict)
    #         self.assertIn('Content-Type', headers)
    #         self.assertIn('Content-Length', headers)
            
    #         params = {'key1': 'item1', 'key2': 'item2'}
    #         headers, body = await client.get('/get', params=params)
    #         self.assertEqual(body['args'], params)
    

    # async def test_post(self):
    #     async with Client(self.loop, HTTPBIN) as client:
    #         headers, body = await client.post('/post')
    #         self.assertEqual(body['form'], {})
    #         self.assertEqual(body['headers']['User-Agent'], USER_AGENT)
    #         self.assertIsInstance(headers, dict)
    #         self.assertIn('Content-Type', headers)
    #         self.assertIn('Content-Length', headers)
            
    #         data = {"key1": "item1", "key2": "item2"}
    #         headers, body = await client.post('/post', data=data)
    #         self.assertEqual(json.loads(body['data']), data)

      
    # async def test_products(self):
        
    #     keys = {'id', 'base_currency', 'quote_currency', 'base_min_size', 
    #             'base_max_size', 'quote_increment', 'display_name', 'status',
    #             'margin_enabled', 'status_message', 'min_market_funds', 
    #             'max_market_funds', 'post_only', 'limit_only', 'cancel_only'}
        
    #     # Sometimes returns 'accesible' as a key. ?? 
        
    #     products = await self.client.products()

    #     self.assertIsInstance(products, list)
    #     self.assertGreater(len(products), 1)
    #     self.assertIsInstance(products[0], dict)
    #     self.assertGreaterEqual(len(products[0]), len(keys))
    #     self.assertLessEqual(products[0].keys(), keys)


    # async def test_order_book(self):
        
    #     keys = {'sequence', 'bids', 'asks'}
        
    #     ob1 = await self.client.order_book('BTC-USD', level=1)
    #     self.assertIsInstance(ob1, dict)
    #     self.assertEqual(ob1.keys(), keys)
    #     self.assertIsInstance(ob1['bids'], list)
    #     self.assertEqual(len(ob1['bids']), 1)
    #     self.assertEqual(len(ob1['bids'][0]), 3)
    #     self.assertIsInstance(ob1['asks'], list)
    #     self.assertEqual(len(ob1['asks']), 1)
    #     self.assertEqual(len(ob1['asks'][0]), 3)
        
    #     ob2 = await self.client.order_book('BTC-USD', level=2)
    #     self.assertIsInstance(ob2, dict)
    #     self.assertEqual(ob2.keys(), keys)
    #     self.assertIsInstance(ob2['bids'], list)
    #     self.assertEqual(len(ob2['bids']), 50)
    #     self.assertEqual(len(ob2['bids'][0]), 3)
    #     self.assertIsInstance(ob2['asks'], list)
    #     self.assertEqual(len(ob2['asks']), 50)
    #     self.assertEqual(len(ob2['asks'][0]), 3)
                
        
    #     ob3 = await self.client.order_book('BTC-USD', level=3)
    #     self.assertIsInstance(ob3, dict)
    #     self.assertEqual(ob3.keys(), keys)
    #     self.assertIsInstance(ob3['bids'], list)
    #     self.assertGreater(len(ob3['bids']), 50)
    #     self.assertEqual(len(ob3['bids'][0]), 3)
    #     self.assertIsInstance(ob3['asks'], list)
    #     self.assertGreater(len(ob3['asks']), 50)
    #     self.assertEqual(len(ob3['asks'][0]), 3)            

    
    # async def test_ticker(self):
        
    #     keys = {'trade_id', 'price', 'size', 'bid', 'ask', 'volume', 'time'}
        
    #     tick = await self.client.ticker('BTC-USD')
    #     self.assertIsInstance(tick, dict)
    #     self.assertEqual(tick.keys(), keys)
        
    
    # async def test_trades(self):
        
    #     keys = {'time', 'trade_id', 'price', 'size', 'side'}
        
    #     trades, before, after = await self.client.trades('BTC-USD')
    #     self.assertIsInstance(trades, list)
    #     self.assertIsInstance(trades[0], dict)
    #     self.assertIsInstance(before, str)
    #     self.assertIsInstance(after, str)
    #     self.assertEqual(len(trades), 100)
    #     self.assertEqual(trades[0].keys(), keys)
            
    #     trades, before, after = await self.client.trades('BTC-USD', 5)
    #     self.assertEqual(len(trades), 5)

    #     trades_after, after_after, before_after = await self.client.trades('BTC-USD', 5, after=after)
    #     self.assertLess(trades_after[0]['trade_id'], trades[-1]['trade_id'])
                
    #     trades_before, after_before, before_before = await self.client.trades('BTC-USD', 5, before=before)
    #     if trades_before:
    #         self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
    #     else:
    #         self.assertIsNone(after_before)
    #         self.assertIsInstance(after_after, str)
            
    #         await asyncio.sleep(20)
    
    #         trades_before, after_before, before_before = await self.client.trades('BTC-USD', 5, before=before)
    #         if (trades_before):
    #             self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
    #         else:
    #             self.assertIsNone(after_before)
    #             self.assertIsInstance(after_after, str)

             
    # async def test_historic_rates(self):
        
    #     rates = await self.client.historic_rates('BTC-USD', 900)
    #     self.assertIsInstance(rates, list)
    #     self.assertEqual(len(rates[0]), 6)
    #     self.assertEqual(rates[0][0] - rates[1][0], 900)
                
    #     stop = datetime.utcnow()
    #     start = stop - timedelta(days=1)
    #     rates = await self.client.historic_rates('LTC-USD', 3600, start.isoformat(), stop.isoformat())
    #     self.assertIsInstance(rates, list)
    #     self.assertEqual(len(rates), 24)
    #     self.assertEqual(len(rates[0]), 6)
    #     self.assertEqual(rates[0][0] - rates[1][0], 3600)
 
        
    # async def test_get_24hour_stats(self):
        
    #     keys = {'open', 'high', 'low', 'volume', 'last', 'volume_30day'}
        
    #     stats = await self.client.get_24hour_stats('BTC-USD')
    #     self.assertIsInstance(stats, dict)
    #     self.assertEqual(stats.keys(), keys)

       
    # async def test_currencies(self):
        
    #     keys = {'id', 'name', 'min_size', 'status', 'message'}
        
    #     currencies = await self.client.currencies()
    #     self.assertIsInstance(currencies, list)
    #     self.assertGreater(len(currencies), 1)
    #     self.assertIsInstance(currencies[0], dict)
    #     self.assertEqual(currencies[0].keys(), keys)

    
    # async def test_server_time(self):
        
    #     time = await self.client.server_time()
    #     self.assertIsInstance(time, dict)
    #     self.assertIn('iso', time)
    #     self.assertIn('epoch', time)
    #     self.assertIsInstance(time['iso'], str)
    #     self.assertIsInstance(time['epoch'], float)
        
        
    # @skipUnless(TEST_AUTH, "Authentication credentials not provided.")
    # async def test_accounts(self):
        
    #     keys = {'id', 'currency', 'balance', 'available', 'hold', 'profile_id'}
        
    #     accounts = await self.auth_client.accounts()
    #     self.assertIsInstance(accounts, list)
    #     self.assertIsInstance(accounts[0], dict)
    #     self.assertGreaterEqual(accounts[0].keys(), keys)
        

    # @skipUnless(TEST_AUTH and TEST_BTC_ACCOUNT, "Auth credentials and test BTC account ID required")
    # async def test_account(self):
        
    #     keys = {'id', 'currency', 'balance', 'available', 'hold', 'profile_id'}
        
    #     account = await self.auth_client.account(TEST_BTC_ACCOUNT)
    #     self.assertIsInstance(account, dict)
    #     self.assertEqual(account.keys(), keys)
    #     self.assertEqual(account['id'], TEST_BTC_ACCOUNT)
    #     self.assertEqual(account['currency'], 'BTC')
            
            
    # # TO DO
    # @expectedFailure
    # @skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    # async def test_get_account_history(self):
    #     assert False
        
    # # TO DO   
    # @expectedFailure
    # @skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    # async def test_holds(self):
    #     assert False
        

    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_limit_order(self):
    #     # Assumes cancel works
    #     for side, base_price in (('buy', 1), ('sell', 10000)):
    #         # default time_in_force
    #         price = base_price + (random.randint(1, 9) / 10)
    #         size = random.randint(1, 10) / 1000
    #         order = await self.auth_client.limit_order(side, 'BTC-USD', 
    #                                                     price=price, size=size)
                                                        
    #         await self.auth_client.cancel(order['id'])
            
    #         keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
    #             'id', 'post_only', 'price', 'product_id', 'settled', 'side', 
    #             'size', 'status', 'stp', 'time_in_force', 'type'}
                
    #         self.assertEqual(order.keys(), keys)
    #         self.assertEqual(float(order['price']), price)
    #         self.assertEqual(float(order['size']), size)
    #         self.assertEqual(order['product_id'], 'BTC-USD')
    #         self.assertEqual(order['side'], side)
    #         self.assertEqual(order['stp'], 'dc')
    #         self.assertEqual(order['type'], 'limit')
    #         self.assertEqual(order['time_in_force'], 'GTC')
            
    #         # client_oid, explicit time_in_force
    #         price = base_price + (random.randint(1, 9) / 10)
    #         size = random.randint(1, 10) / 1000
    #         client_oid = str(uuid4())
    #         order = await self.auth_client.limit_order(side, 'BTC-USD', 
    #                                           price=price, size=size, 
    #                                           time_in_force='GTC',
    #                                           client_oid=client_oid)
            
    #         await self.auth_client.cancel(order['id'])
            
    #         self.assertEqual(order.keys(), keys)
    #         self.assertEqual(float(order['price']), price)
    #         self.assertEqual(float(order['size']), size)
    #         self.assertEqual(order['product_id'], 'BTC-USD')
    #         self.assertEqual(order['side'], side)
    #         self.assertEqual(order['stp'], 'dc')
    #         self.assertEqual(order['type'], 'limit')
    #         self.assertEqual(order['time_in_force'], 'GTC')
            
            
    #         # IOC time_in_force
    #         price = base_price + (random.randint(1, 9) / 10)
    #         size = random.randint(1, 10) / 1000
                
    #         order = await self.auth_client.limit_order(side, 'BTC-USD', 
    #                                                   price=price, size=size,
    #                                                   time_in_force='IOC')
            
    #         try:
    #             await self.auth_client.cancel(order['id'])
    #         except APIRequestError:
    #             pass
            
    #         self.assertEqual(order.keys(), keys)
    #         self.assertEqual(float(order['price']), price)
    #         self.assertEqual(float(order['size']), size)
    #         self.assertEqual(order['product_id'], 'BTC-USD')
    #         self.assertEqual(order['side'], side)
    #         self.assertEqual(order['stp'], 'dc')
    #         self.assertEqual(order['type'], 'limit')
    #         self.assertEqual(order['time_in_force'], 'IOC')
            
    #         # FOK time_in_force
    #         price = base_price + (random.randint(1, 9) / 10)
    #         size = random.randint(1, 10) / 1000
                
    #         order = await self.auth_client.limit_order(side, 'BTC-USD', 
    #                                                   price=price, size=size,
    #                                                   time_in_force='FOK')

    #         if 'reject_reason' in order:
    #             keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
    #                 'id', 'post_only', 'price', 'product_id', 'reject_reason', 
    #                 'settled', 'side', 'size', 'status', 'time_in_force', 
    #                 'type'}
                    
    #         try:
    #             await self.auth_client.cancel(order['id'])
    #         except APIRequestError:
    #             pass
    
    #         self.assertEqual(order.keys(), keys)
    #         self.assertEqual(float(order['price']), price)
    #         self.assertEqual(float(order['size']), size)
    #         self.assertEqual(order['product_id'], 'BTC-USD')
    #         self.assertEqual(order['side'], side)
    #         self.assertEqual(order['type'], 'limit')
    #         self.assertEqual(order['time_in_force'], 'FOK')
            
    #         # GTT time_in_force, iterate cancel_after
    #         for ca_str, ca_int in [('min', 60), ('hour', 3600), ('day', 86400)]:
    #             o_time = await self.client.server_time()
    #             o_time = float(o_time['epoch'])
        
    #             price = base_price + (random.randint(1, 9) / 10)
    #             size = random.randint(1, 10) / 1000
                
    #             order = await self.auth_client.limit_order(side, 'BTC-USD', 
    #                                                      price=price, size=size, 
    #                                                      time_in_force='GTT',  
    #                                                      cancel_after=ca_str)
                                            
    #             await self.auth_client.cancel(order['id'])
                
    #             keys = {'created_at', 'executed_value', 'expire_time', 'fill_fees', 
    #                 'filled_size', 'id', 'post_only', 'price', 'product_id', 'settled', 
    #                 'side', 'size', 'status', 'stp', 'time_in_force', 'type'}
                    
    #             self.assertEqual(order.keys(), keys)
    #             self.assertEqual(float(order['price']), price)
    #             self.assertEqual(float(order['size']), size)
    #             self.assertEqual(order['product_id'], 'BTC-USD')
    #             self.assertEqual(order['side'], side)
    #             self.assertEqual(order['stp'], 'dc')
    #             self.assertEqual(order['type'], 'limit')
    #             self.assertEqual(order['time_in_force'], 'GTT')
    #             e_time = parser.parse(order['expire_time']).timestamp()
    #             self.assertLessEqual(e_time - o_time - ca_int, 1.0)
                

    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_limit_order_stop(self):
        # Assumes cancel works
        
        #stop loss
        order = await self.auth_client.limit_order('sell', 'BTC-USD', 2.1, .001,
                                                    stop='loss', stop_price=2.5)
        
        try:
            await self.auth_client.cancel(order['id'])
        except APIRequestError:
            pass
        
        keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                'id', 'post_only', 'price', 'product_id', 'settled', 'side', 
                'size', 'status', 'stp', 'time_in_force', 'type', 'stop',
                'stop_price'}
                
        self.assertEqual(order.keys(), keys)
        self.assertEqual(float(order['price']), 2.1)
        self.assertEqual(float(order['size']), .001)
        self.assertEqual(order['product_id'], 'BTC-USD')
        self.assertEqual(order['side'], 'sell')
        self.assertEqual(order['stp'], 'dc')
        self.assertEqual(order['type'], 'limit')
        self.assertEqual(order['time_in_force'], 'GTC')
        self.assertEqual(order['stop'], 'loss')
        self.assertEqual(float(order['stop_price']), 2.5)
        
        #stop entry
        order = await self.auth_client.limit_order('buy', 'BTC-USD', 9000, .001,
                                                  stop='entry', stop_price=9550)
        
        try:
            await self.auth_client.cancel(order['id'])
        except APIRequestError:
            pass
        
        keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                'id', 'post_only', 'price', 'product_id', 'settled', 'side', 
                'size', 'status', 'stp', 'time_in_force', 'type', 'stop',
                'stop_price'}
                
        self.assertEqual(order.keys(), keys)
        self.assertEqual(float(order['price']), 9000)
        self.assertEqual(float(order['size']), .001)
        self.assertEqual(order['product_id'], 'BTC-USD')
        self.assertEqual(order['side'], 'buy')
        self.assertEqual(order['stp'], 'dc')
        self.assertEqual(order['type'], 'limit')
        self.assertEqual(order['time_in_force'], 'GTC')
        self.assertEqual(order['stop'], 'entry')
        self.assertEqual(float(order['stop_price']), 9550)
    
    
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_market_order(self):
    #     # Assumes cancel works
    #     for side in ('buy', 'sell'):
    #         # Size
    #         size = random.randint(1, 10) / 1000
            
    #         order = await self.auth_client.market_order(side, 'BTC-USD', size=size)

    #         keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
    #                 'funds', 'id', 'post_only', 'product_id', 'settled', 'side', 
    #                 'size', 'status', 'stp', 'type'}
                    
    #         if side == 'sell':
    #             keys.remove('funds')
    
    #         self.assertEqual(order.keys(), keys)
    #         self.assertEqual(float(order['size']), size)
    #         self.assertEqual(order['product_id'], 'BTC-USD')
    #         self.assertEqual(order['side'], side)
    #         self.assertEqual(order['stp'], 'dc')
    #         self.assertEqual(order['type'], 'market')
    #         self.assertEqual(order['post_only'], False)
            
    #         await asyncio.sleep(.5)
            
    #         # Funds
    #         funds = 100 + random.randint(1, 10)
            
    #         order = await self.auth_client.market_order(side, 'BTC-USD', funds=funds)
                                               
    #         keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
    #                 'funds', 'id', 'post_only', 'product_id', 'settled', 'side', 
    #                 'specified_funds', 'status', 'stp', 'type'}
                    
    #         if side == 'sell':
    #             keys.add('size')

    #         self.assertEqual(order.keys(), keys)
    #         self.assertEqual(order['product_id'], 'BTC-USD')
    #         self.assertEqual(order['side'], side)
    #         self.assertEqual(order['stp'], 'dc')
    #         self.assertEqual(float(order['specified_funds']), funds)
    #         self.assertEqual(order['type'], 'market')
    #         self.assertEqual(order['post_only'], False)
            
    #         await asyncio.sleep(.5)
            
    #     #client_oid
    #     client_oid = str(uuid4())
    #     order = await self.auth_client.market_order('sell', 'BTC-USD', funds=100,
    #                                               client_oid=client_oid, stp='dc')
    #     self.assertEqual(order.keys(), keys)
        
    #     self.assertEqual(order.keys(), keys)
    #     self.assertEqual(order['product_id'], 'BTC-USD')
    #     self.assertEqual(order['side'], side)
    #     self.assertEqual(order['stp'], 'dc')
    #     self.assertEqual(float(order['funds']), 100)
    #     self.assertEqual(order['type'], 'market')
    #     self.assertEqual(order['post_only'], False)
        
    #     await asyncio.sleep(.5)
        
    #     # This really shouldn't raise an error, but as of 11/18, the Coinbase
    #     # sandbox won't accept an stp other dc even though the Coinbase API
    #     # documentation claims otherwise.
    #     with self.assertRaises(APIRequestError):
    #         order = await self.auth_client.market_order('sell', 'BTC-USD', 
    #                                   funds=100, client_oid=client_oid, stp='cb')
    
    
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_market_order_stop(self):
    #     # Assumes cancel works

    #     # stop loss
    #     order = await self.auth_client.market_order('sell', 'BTC-USD', .001,
    #                                                 stop='loss', stop_price=2.5)
        
    #     try:
    #         await self.auth_client.cancel(order['id'])
    #     except APIRequestError:
    #         pass
        
        
    #     keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
    #             'id', 'post_only', 'product_id', 'settled', 'side', 'size', 
    #             'status', 'stop', 'stop_price', 'stp', 'type'}
                
    #     self.assertEqual(order.keys(), keys)
    #     self.assertEqual(float(order['size']), .001)
    #     self.assertEqual(order['product_id'], 'BTC-USD')
    #     self.assertEqual(order['side'], 'sell')
    #     self.assertEqual(order['stp'], 'dc')
    #     self.assertEqual(order['type'], 'market')
    #     self.assertEqual(order['post_only'], False)
    #     self.assertEqual(order['stop'], 'loss')
    #     self.assertEqual(float(order['stop_price']), 2.5)
        
    #     await asyncio.sleep(0.5)
        
    #     # stop entry
    #     order = await self.auth_client.market_order('buy', 'BTC-USD', .001,
    #                                              stop='entry', stop_price=10000)

    #     try:
    #         await self.auth_client.cancel(order['id'])
    #     except APIRequestError:
    #         pass
        
    #     keys =  {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
    #             'funds', 'id', 'post_only', 'product_id', 'settled', 'side', 
    #             'size', 'status', 'stop', 'stop_price', 'stp', 'type'}
        
    #     self.assertEqual(order.keys(), keys)
    #     self.assertEqual(float(order['size']), .001)
    #     self.assertEqual(order['product_id'], 'BTC-USD')
    #     self.assertEqual(order['side'], 'buy')
    #     self.assertEqual(order['stp'], 'dc')
    #     self.assertEqual(order['type'], 'market')
    #     self.assertEqual(order['post_only'], False)
    #     self.assertEqual(order['stop'], 'entry')
    #     self.assertEqual(float(order['stop_price']), 10000)
        
    
    # # TO DO   
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_cancel(self):
    #     assert False
        
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_cancel_all(self):
    #     # Assumes place_order and orders work
    #     resp = await self.auth_client.cancel_all()
    #     orders, _, _ = await self.auth_client.orders('open')
    #     self.assertEqual(len(orders), 0)
        
    #     await asyncio.sleep(0.5)
        
    #     for price in (1, 2, 3):
    #         order = await self.auth_client.place_order('buy', 'BTC-USD', 
    #                                                   price=price, size=1)
    #         await asyncio.sleep(0.5)
            
    #     for price in (10000, 20000, 30000):
    #         order = await self.auth_client.place_order('sell', 'BTC-USD', 
    #                                                   price=price, size=0.01)
    #         await asyncio.sleep(0.5)    
        
    #     orders, _, _ = await self.auth_client.orders('open')
    #     self.assertEqual(len(orders), 6)
    #     resp = await self.auth_client.cancel_all()
    #     orders, _, _ = await self.auth_client.orders('open')
    #     self.assertEqual(len(orders), 0)
        

    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_orders(self):
    #     # Assumes place_order and cancel_all work
    #     await self.auth_client.cancel_all()
    #     open_orders, _, _, = await self.auth_client.orders('open')
    #     self.assertEqual(len(open_orders), 0)
        
    #     open_ids = []
    #     for price in (1.0, 1.1):
    #         order = await self.auth_client.place_order('buy', 'BTC-USD', 
    #                                                   price=price, size=1)
    #         open_ids.append(order['id'])
            
    #     open_orders, _, _ = await self.auth_client.orders('open')
    #     self.assertEqual(len(open_orders), 2)
    #     self.assertEqual(open_orders[0]['id'], open_ids[1])
    #     self.assertEqual(open_orders[1]['id'], open_ids[0])
        
    #     market_ids = []
    #     for _ in range(2):
    #         order = await self.auth_client.place_order('buy', 'BTC-USD',
    #                                             order_type='market', size=0.01)
    #         market_ids.append(order['id'])
        
    #     all_orders, _, _, = await self.auth_client.orders('all')
    #     self.assertGreaterEqual(len(all_orders), 4)
    #     self.assertEqual(all_orders[0]['id'], market_ids[1])
    #     self.assertEqual(all_orders[1]['id'], market_ids[0])
    #     self.assertEqual(all_orders[2]['id'], open_ids[1])
    #     self.assertEqual(all_orders[3]['id'], open_ids[0])
        
    #     await self.auth_client.cancel_all()
    #     open_orders, _, _, = await self.auth_client.orders('open')
    #     self.assertEqual(len(open_orders), 0)
        

    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_order(self):
    #     # Assumes place order works
    #     open_ids = []
    #     for price in (1.1, 1.2, 1.3):
    #         order = await self.auth_client.place_order('buy', 'BTC-USD', 
    #                                                   price=price, size=1)
    #         open_ids.append(order['id'])
            
    #     order = await self.auth_client.order(open_ids[1])
        
    #     await self.auth_client.cancel_all()
        
        
    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_fills(self):
    #     assert False
        

    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_payment_methods(self):
    #     keys = {'id', 'type', 'name', 'currency', 'primary_buy', 'primary_sell',
    #             'allow_buy', 'allow_sell', 'allow_deposit', 'allow_withdraw',
    #             'limits'}

    #     methods = await self.auth_client.payment_methods()
    #     self.assertIsInstance(methods, list)
    #     self.assertIsInstance(methods[0], dict)
    #     self.assertGreaterEqual(methods[0].keys(), keys)
        

    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_coinbase_accounts(self):
    #     keys =  {'id', 'name', 'balance', 'currency', 'type', 'primary', 'active'}
        
    #     accounts = await self.auth_client.coinbase_accounts()
    #     self.assertIsInstance(accounts, list)
    #     self.assertIsInstance(accounts[0], dict)
    #     self.assertGreaterEqual(accounts[0].keys(), keys)
        
        
    # @skipUnless(TEST_AUTH and TEST_USD_ACCOUNT and TEST_USD_DEPOSIT_METHOD,
    # "Auth credentials, test USD account, and test USD payment method required.")
    # async def test_deposit_payment_method(self):
    #     # Presupposes that rest.Client.account() works properly
    #     usd_account = await self.auth_client.account(TEST_USD_ACCOUNT)
    #     pre_usd_balance = usd_account['balance']
    #     print(pre_usd_balance)
        
    #     deposit = await self.auth_client.deposit_payment_method(1500, 'USD', 
    #                                                     TEST_USD_DEPOSIT_METHOD)
                                                        
    #     print(deposit)


    # @skipUnless(TEST_AUTH and TEST_USD_ACCOUNT and TEST_USD_COINBASE_ACCOUNT, 
    # "Auth credentials, test USD account, and test usd Coinbase account  required")
    # async def test_deposit_cointbase(self):
    #     deposit = await self.auth_client.deposit_coinbase(150, 'USD',
    #                                               TEST_USD_COINBASE_ACCOUNT)
    #     print(deposit)


    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_withdraw_payment_method(self):
    #     assert False
        
    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_withdraw_cointbase(self):
    #     assert False
        
    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_withdraw_crypto(self):
    #     assert False
        
    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_stablecoin_conversion(self):
    #     assert False
        
    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_create_report(self):
    #     assert False
        
    # # TO DO
    # @expectedFailure 
    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_report_status(self):
    #     assert False
        

    # @skipUnless(TEST_AUTH, "Auth credentials required")
    # async def test_trailing_volume (self):
    #     tv = await self.auth_client.trailing_volume()
