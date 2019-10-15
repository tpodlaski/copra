#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.rest.Client` class.

Without any additional user input, this module will test all of the 
unauthenticated methods of the copra.rest.Client.

An API key for the Coinbase Pro sandbox is required to test the authenticated
methods. The key information as well as the ids of a few test accounts are 
read in to this module as environment variables by the dotenv module from a
file named .env. The .env file must reside in the same directory as this test 
module.

An example .env file named .env.sample is provided. To test the authenticated
methods, fill out the .env.sample file accordingly and rename it to .env.
"""

import os.path
if os.path.isfile(os.path.join(os.path.dirname(__file__), '.env')):
    from dotenv import load_dotenv
    load_dotenv()
else:
    print("\n** .env file not found. Authenticated methods will be skipped. **\n")
    
import asyncio
from datetime import datetime, timedelta
import os
import json
import random
import time
from uuid import uuid4

from asynctest import TestCase, skipUnless, expectedFailure
from dateutil import parser

from copra.rest import APIRequestError, Client, SANDBOX_URL
from copra.rest.client import USER_AGENT

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PASSPHRASE = os.getenv('PASSPHRASE')
TEST_AUTH = True if (KEY and SECRET and PASSPHRASE) else False
TEST_BTC_ACCOUNT = os.getenv('TEST_BTC_ACCOUNT')
TEST_USD_ACCOUNT = os.getenv('TEST_USD_ACCOUNT')
TEST_USD_PAYMENT_METHOD = os.getenv('TEST_USD_PAYMENT_METHOD')
TEST_USD_COINBASE_ACCOUNT = os.getenv('TEST_USD_COINBASE_ACCOUNT')

HTTPBIN = 'http://httpbin.org'

class TestRest(TestCase):
    """Tests for copra.rest.Client"""
    
    def setUp(self):
        self.client = Client(self.loop)
        if TEST_AUTH:
            self.auth_client = Client(self.loop, SANDBOX_URL, auth=True, 
                                      key=KEY, secret=SECRET, 
                                      passphrase=PASSPHRASE)
     
                                  
    def tearDown(self):
        self.loop.create_task(self.client.close())
        if TEST_AUTH:
            self.loop.run_until_complete(self.auth_client.cancel_all(stop=True))
            self.loop.create_task(self.auth_client.close())
        # try to avoid public rate limit, allow for aiohttp cleanup and
        # all outstanding Coinbase actions to complete
        self.loop.run_until_complete(asyncio.sleep(1))
        
        
    async def test_user_agent(self):
        
        async with Client(self.loop, HTTPBIN) as client:
            headers, body = await client.get('/user-agent')
            self.assertEqual(body['user-agent'], USER_AGENT)

    
    async def test__handle_error(self):
        async with Client(self.loop, HTTPBIN) as client:
        
            with self.assertRaises(APIRequestError) as cm:
                headers, body = await client.get('/status/404')
                

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
            body['args'].pop('no-cache', None)
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

      
    async def test_products(self):
        
        keys = {'id', 'base_currency', 'quote_currency', 'base_min_size', 
                'base_max_size', 'quote_increment', 'display_name', 'status',
                'margin_enabled', 'status_message', 'min_market_funds', 
                'max_market_funds', 'post_only', 'limit_only', 'cancel_only'}
        
        # Sometimes returns 'accesible' as a key. ?? 
        
        products = await self.client.products()

        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 1)
        self.assertIsInstance(products[0], dict)
        self.assertGreaterEqual(len(products[0]), len(keys))
        self.assertGreaterEqual(products[0].keys(), keys)


    async def test_order_book(self):
        
        keys = {'sequence', 'bids', 'asks'}
        
        ob1 = await self.client.order_book('BTC-USD', level=1)
        self.assertIsInstance(ob1, dict)
        self.assertEqual(ob1.keys(), keys)
        self.assertIsInstance(ob1['bids'], list)
        self.assertEqual(len(ob1['bids']), 1)
        self.assertEqual(len(ob1['bids'][0]), 3)
        self.assertIsInstance(ob1['asks'], list)
        self.assertEqual(len(ob1['asks']), 1)
        self.assertEqual(len(ob1['asks'][0]), 3)
        
        ob2 = await self.client.order_book('BTC-USD', level=2)
        self.assertIsInstance(ob2, dict)
        self.assertEqual(ob2.keys(), keys)
        self.assertIsInstance(ob2['bids'], list)
        self.assertEqual(len(ob2['bids']), 50)
        self.assertEqual(len(ob2['bids'][0]), 3)
        self.assertIsInstance(ob2['asks'], list)
        self.assertEqual(len(ob2['asks']), 50)
        self.assertEqual(len(ob2['asks'][0]), 3)
                
        
        ob3 = await self.client.order_book('BTC-USD', level=3)
        self.assertIsInstance(ob3, dict)
        self.assertEqual(ob3.keys(), keys)
        self.assertIsInstance(ob3['bids'], list)
        self.assertGreater(len(ob3['bids']), 50)
        self.assertEqual(len(ob3['bids'][0]), 3)
        self.assertIsInstance(ob3['asks'], list)
        self.assertGreater(len(ob3['asks']), 50)
        self.assertEqual(len(ob3['asks'][0]), 3)            

    
    async def test_ticker(self):
        
        keys = {'trade_id', 'price', 'size', 'bid', 'ask', 'volume', 'time'}
        
        tick = await self.client.ticker('BTC-USD')
        self.assertIsInstance(tick, dict)
        self.assertEqual(tick.keys(), keys)
        
    
    async def test_trades(self):
        
        keys = {'time', 'trade_id', 'price', 'size', 'side'}
        
        trades, before, after = await self.client.trades('BTC-USD')
        self.assertIsInstance(trades, list)
        self.assertIsInstance(trades[0], dict)
        self.assertIsInstance(before, str)
        self.assertIsInstance(after, str)
        self.assertEqual(len(trades), 100)
        self.assertEqual(trades[0].keys(), keys)
            
        trades, before, after = await self.client.trades('BTC-USD', 5)
        self.assertEqual(len(trades), 5)

        trades_after, after_after, before_after = await self.client.trades('BTC-USD', 5, after=after)
        self.assertLess(trades_after[0]['trade_id'], trades[-1]['trade_id'])
                
        trades_before, after_before, before_before = await self.client.trades('BTC-USD', 5, before=before)
        if trades_before:
            self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
        else:
            self.assertIsNone(after_before)
            self.assertIsInstance(after_after, str)
            
            await asyncio.sleep(20)
    
            trades_before, after_before, before_before = await self.client.trades('BTC-USD', 5, before=before)
            if (trades_before):
                self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
            else:
                self.assertIsNone(after_before)
                self.assertIsInstance(after_after, str)

             
    async def test_historic_rates(self):
        
        rates = await self.client.historic_rates('BTC-USD', 900)
        self.assertIsInstance(rates, list)
        self.assertEqual(len(rates[0]), 6)
        self.assertEqual(rates[0][0] - rates[1][0], 900)
                
        end = datetime.utcnow()
        start = end - timedelta(days=1)
        rates = await self.client.historic_rates('LTC-USD', 3600, start.isoformat(), end.isoformat())
        self.assertIsInstance(rates, list)
        self.assertEqual(len(rates), 24)
        self.assertEqual(len(rates[0]), 6)
        self.assertEqual(rates[0][0] - rates[1][0], 3600)
 
        
    async def test_get_24hour_stats(self):
        
        keys = {'open', 'high', 'low', 'volume', 'last', 'volume_30day'}
        
        stats = await self.client.get_24hour_stats('BTC-USD')
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats.keys(), keys)

       
    async def test_currencies(self):
        
        keys = {'id', 'name', 'min_size', 'status', 'message', 'details'}
        
        currencies = await self.client.currencies()
        self.assertIsInstance(currencies, list)
        self.assertGreater(len(currencies), 1)
        self.assertIsInstance(currencies[0], dict)
        self.assertEqual(currencies[0].keys(), keys)

    
    async def test_server_time(self):
        
        time = await self.client.server_time()
        self.assertIsInstance(time, dict)
        self.assertIn('iso', time)
        self.assertIn('epoch', time)
        self.assertIsInstance(time['iso'], str)
        self.assertIsInstance(time['epoch'], float)
        
        
    @skipUnless(TEST_AUTH, "Authentication credentials not provided.")
    async def test_accounts(self):
        
        keys = {'id', 'currency', 'balance', 'available', 'hold', 'profile_id'}
        
        accounts = await self.auth_client.accounts()
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], dict)
        self.assertGreaterEqual(accounts[0].keys(), keys)
        

    @skipUnless(TEST_AUTH and TEST_BTC_ACCOUNT, "Auth credentials and test BTC account ID required")
    async def test_account(self):
        
        keys = {'id', 'currency', 'balance', 'available', 'hold', 'profile_id'}
        
        account = await self.auth_client.account(TEST_BTC_ACCOUNT)
        self.assertIsInstance(account, dict)
        self.assertEqual(account.keys(), keys)
        self.assertEqual(account['id'], TEST_BTC_ACCOUNT)
        self.assertEqual(account['currency'], 'BTC')
            
            
    @skipUnless(TEST_AUTH and TEST_BTC_ACCOUNT, "Auth credentials and test BTC account ID required")
    async def test_account_history(self):
        # Assumes market_order works.
        
        orders = []
        for i in range(1,6):
            size = 0.001 * i
            order = await self.auth_client.market_order('buy', 'BTC-USD', size)
            orders.append(order)
            await asyncio.sleep(0.25)
        
        history, before, after = await self.auth_client.account_history(
                                                          TEST_BTC_ACCOUNT, limit=3)
            
        keys = {'amount', 'balance', 'created_at', 'details', 'id', 'type'}
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].keys(), keys)
        self.assertEqual(history[0]['type'], 'match')
        self.assertEqual(history[0]['details']['order_id'], orders[4]['id'])
        self.assertEqual(history[0]['details']['product_id'], 'BTC-USD')
            
        after_history, after_before, after_after =  await self.auth_client.account_history(TEST_BTC_ACCOUNT, after=after)
        self.assertGreater(history[-1]['id'], after_history[0]['id'])
                
        original_history, _, _ = await self.auth_client.account_history(TEST_BTC_ACCOUNT, before=after_before)
        self.assertEqual(original_history, history)
            
        
    @skipUnless(TEST_AUTH and TEST_BTC_ACCOUNT, "Auth credentials and test BTC account ID required")
    async def test_holds(self):
        # Assumes cancel, cancel_all and limit_order work
        
        await self.auth_client.cancel_all(stop=True)
        holds, _, _ = await self.auth_client.holds(TEST_BTC_ACCOUNT)
        offset = len(holds)

        orders = []
        for i in range(1, 8):
            size = .001 * i
            price = 10000 + i * 1000
            order = await self.auth_client.limit_order('sell', 'BTC-USD', price, size)
            orders.append(order)
            await asyncio.sleep(.25)
            
        holds, _, _ = await self.auth_client.holds(TEST_BTC_ACCOUNT)

        keys = {'amount', 'created_at', 'id', 'ref', 'type'}
        self.assertEqual(len(holds), 7 + offset)
        self.assertEqual(holds[0].keys(), keys)
        self.assertEqual(float(holds[0]['amount']), .007)
        self.assertEqual(orders[6]['id'], holds[0]['ref'])
        
        holds, before, after = await self.auth_client.holds(TEST_BTC_ACCOUNT, 
                                                                        limit=5)
        self.assertEqual(len(holds), 5)
        
        after_holds, after_before, after_after =  await self.auth_client.holds(
                                                  TEST_BTC_ACCOUNT, after=after)
        self.assertEqual(len(after_holds), 2 + offset)
        
        original_holds, _, _ = await self.auth_client.holds(TEST_BTC_ACCOUNT,
                                                  before=after_before, limit=5)
        self.assertEqual(original_holds, holds)
        
        for order in orders[4:]:
            resp = await self.auth_client.cancel(order['id'])
            self.assertEqual(resp[0], order['id'])
            
        holds, _, _ = await self.auth_client.holds(TEST_BTC_ACCOUNT)
        
        total = 0
        for hold in holds:
            if hold['type'] == 'order':
                total += float(hold['amount'])
        self.assertAlmostEqual(total, 0.01)
        

    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_limit_order(self):
        # Assumes cancel works
        for side, base_price in (('buy', 1), ('sell', 50000)):
            # default time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            order = await self.auth_client.limit_order(side, 'BTC-USD', 
                                                        price=price, size=size)
                                                        
            await self.auth_client.cancel(order['id'])
            
            keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                'id', 'post_only', 'price', 'product_id', 'settled', 'side', 
                'size', 'status', 'stp', 'time_in_force', 'type'}
                
            self.assertEqual(order.keys(), keys)
            self.assertEqual(float(order['price']), price)
            self.assertEqual(float(order['size']), size)
            self.assertEqual(order['product_id'], 'BTC-USD')
            self.assertEqual(order['side'], side)
            self.assertEqual(order['stp'], 'dc')
            self.assertEqual(order['type'], 'limit')
            self.assertEqual(order['time_in_force'], 'GTC')
            
            # client_oid, explicit time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            client_oid = str(uuid4())
            order = await self.auth_client.limit_order(side, 'BTC-USD', 
                                              price=price, size=size, 
                                              time_in_force='GTC',
                                              client_oid=client_oid)
            
            await self.auth_client.cancel(order['id'])
            
            self.assertEqual(order.keys(), keys)
            self.assertEqual(float(order['price']), price)
            self.assertEqual(float(order['size']), size)
            self.assertEqual(order['product_id'], 'BTC-USD')
            self.assertEqual(order['side'], side)
            self.assertEqual(order['stp'], 'dc')
            self.assertEqual(order['type'], 'limit')
            self.assertEqual(order['time_in_force'], 'GTC')
            
            
            # IOC time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
                
            order = await self.auth_client.limit_order(side, 'BTC-USD', 
                                                      price=price, size=size,
                                                      time_in_force='IOC')
            
            try:
                await self.auth_client.cancel(order['id'])
            except APIRequestError:
                pass
            
            self.assertEqual(order.keys(), keys)
            self.assertEqual(float(order['price']), price)
            self.assertEqual(float(order['size']), size)
            self.assertEqual(order['product_id'], 'BTC-USD')
            self.assertEqual(order['side'], side)
            self.assertEqual(order['stp'], 'dc')
            self.assertEqual(order['type'], 'limit')
            self.assertEqual(order['time_in_force'], 'IOC')
            
            # FOK time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
                
            order = await self.auth_client.limit_order(side, 'BTC-USD', 
                                                      price=price, size=size,
                                                      time_in_force='FOK')

            if 'reject_reason' in order:
                keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                    'id', 'post_only', 'price', 'product_id', 'reject_reason', 
                    'settled', 'side', 'size', 'status', 'time_in_force', 
                    'type'}
                    
            try:
                await self.auth_client.cancel(order['id'])
            except APIRequestError:
                pass
    
            self.assertEqual(order.keys(), keys)
            self.assertEqual(float(order['price']), price)
            self.assertEqual(float(order['size']), size)
            self.assertEqual(order['product_id'], 'BTC-USD')
            self.assertEqual(order['side'], side)
            self.assertEqual(order['type'], 'limit')
            self.assertEqual(order['time_in_force'], 'FOK')
            
            # GTT time_in_force, iterate cancel_after
            for ca_str, ca_int in [('min', 60), ('hour', 3600), ('day', 86400)]:
                o_time = await self.client.server_time()
                o_time = float(o_time['epoch'])
        
                price = base_price + (random.randint(1, 9) / 10)
                size = random.randint(1, 10) / 1000
                
                order = await self.auth_client.limit_order(side, 'BTC-USD', 
                                                         price=price, size=size, 
                                                         time_in_force='GTT',  
                                                         cancel_after=ca_str)
                                            
                await self.auth_client.cancel(order['id'])
                
                keys = {'created_at', 'executed_value', 'expire_time', 'fill_fees', 
                    'filled_size', 'id', 'post_only', 'price', 'product_id', 'settled', 
                    'side', 'size', 'status', 'stp', 'time_in_force', 'type'}
                    
                self.assertEqual(order.keys(), keys)
                self.assertEqual(float(order['price']), price)
                self.assertEqual(float(order['size']), size)
                self.assertEqual(order['product_id'], 'BTC-USD')
                self.assertEqual(order['side'], side)
                self.assertEqual(order['stp'], 'dc')
                self.assertEqual(order['type'], 'limit')
                self.assertEqual(order['time_in_force'], 'GTT')
                e_time = parser.parse(order['expire_time']).timestamp()
                self.assertLessEqual(e_time - o_time - ca_int, 1.0)
                

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
    
    
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_market_order(self):
        # Assumes cancel works
        for side in ('buy', 'sell'):
            # Size
            size = random.randint(1, 10) / 1000
            
            order = await self.auth_client.market_order(side, 'BTC-USD', size=size)

            keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                    'funds', 'id', 'post_only', 'product_id', 'settled', 'side', 
                    'size', 'status', 'stp', 'type'}
                    
            if side == 'sell':
                keys.remove('funds')
    
            self.assertEqual(order.keys(), keys)
            self.assertEqual(float(order['size']), size)
            self.assertEqual(order['product_id'], 'BTC-USD')
            self.assertEqual(order['side'], side)
            self.assertEqual(order['stp'], 'dc')
            self.assertEqual(order['type'], 'market')
            self.assertEqual(order['post_only'], False)
            
            await asyncio.sleep(.5)
            
            # Funds
            funds = 100 + random.randint(1, 10)
            
            order = await self.auth_client.market_order(side, 'BTC-USD', funds=funds)
                                               
            keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                    'funds', 'id', 'post_only', 'product_id', 'settled', 'side', 
                    'specified_funds', 'status', 'stp', 'type'}
                    
            if side == 'sell':
                keys.add('size')

            self.assertEqual(order.keys(), keys)
            self.assertEqual(order['product_id'], 'BTC-USD')
            self.assertEqual(order['side'], side)
            self.assertEqual(order['stp'], 'dc')
            self.assertEqual(float(order['specified_funds']), funds)
            self.assertEqual(order['type'], 'market')
            self.assertEqual(order['post_only'], False)
            
            await asyncio.sleep(.5)
            
        #client_oid
        client_oid = str(uuid4())
        order = await self.auth_client.market_order('sell', 'BTC-USD', funds=100,
                                                  client_oid=client_oid, stp='dc')
        self.assertEqual(order.keys(), keys)
        
        self.assertEqual(order.keys(), keys)
        self.assertEqual(order['product_id'], 'BTC-USD')
        self.assertEqual(order['side'], side)
        self.assertEqual(order['stp'], 'dc')
        self.assertEqual(float(order['funds']), 100)
        self.assertEqual(order['type'], 'market')
        self.assertEqual(order['post_only'], False)
        
        await asyncio.sleep(.5)
        
        # This really shouldn't raise an error, but as of 11/18, the Coinbase
        # sandbox won't accept an stp other dc even though the Coinbase API
        # documentation claims otherwise.
        with self.assertRaises(APIRequestError):
            order = await self.auth_client.market_order('sell', 'BTC-USD', 
                                      funds=100, client_oid=client_oid, stp='cb')
    
    
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_market_order_stop(self):
        # Assumes cancel works

        # stop loss
        order = await self.auth_client.market_order('sell', 'BTC-USD', .001,
                                                    stop='loss', stop_price=2.5)
        
        try:
            await self.auth_client.cancel(order['id'])
        except APIRequestError:
            pass
        
        
        keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                'id', 'post_only', 'product_id', 'settled', 'side', 'size', 
                'status', 'stop', 'stop_price', 'stp', 'type'}
                
        self.assertEqual(order.keys(), keys)
        self.assertEqual(float(order['size']), .001)
        self.assertEqual(order['product_id'], 'BTC-USD')
        self.assertEqual(order['side'], 'sell')
        self.assertEqual(order['stp'], 'dc')
        self.assertEqual(order['type'], 'market')
        self.assertEqual(order['post_only'], False)
        self.assertEqual(order['stop'], 'loss')
        self.assertEqual(float(order['stop_price']), 2.5)
        
        await asyncio.sleep(0.5)
        
        # stop entry
        order = await self.auth_client.market_order('buy', 'BTC-USD', .001,
                                                 stop='entry', stop_price=10000)

        try:
            await self.auth_client.cancel(order['id'])
        except APIRequestError:
            pass
        
        keys =  {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
                'funds', 'id', 'post_only', 'product_id', 'settled', 'side', 
                'size', 'status', 'stop', 'stop_price', 'stp', 'type'}
        
        self.assertEqual(order.keys(), keys)
        self.assertEqual(float(order['size']), .001)
        self.assertEqual(order['product_id'], 'BTC-USD')
        self.assertEqual(order['side'], 'buy')
        self.assertEqual(order['stp'], 'dc')
        self.assertEqual(order['type'], 'market')
        self.assertEqual(order['post_only'], False)
        self.assertEqual(order['stop'], 'entry')
        self.assertEqual(float(order['stop_price']), 10000)
        
    
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_cancel(self):
        # Assumes limit_order and market_order work.
        
        l_order = await self.auth_client.limit_order('buy', 'BTC-USD', 
                                                     price=1, size=1)
                                                     
        m_order = await self.auth_client.market_order('sell', 'BTC-USD', .001)
        
        s_order = await self.auth_client.limit_order('sell', 'BTC-USD', 2, 5,
                                                     stop='loss', stop_price=10)
                                                     
        resp = await self.auth_client.cancel(l_order['id'])
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], l_order['id'])
        
        with self.assertRaises(APIRequestError):
            await self.auth_client.cancel(m_order['id'])
            
        resp = await self.auth_client.cancel(s_order['id'])
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0], s_order['id'])
            
        
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_cancel_all(self):
        # Assumes market_order, limit_order, and orders work
        await self.auth_client.cancel_all(stop=True)
        orders, _, _ = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(orders), 0)
        
        await asyncio.sleep(0.5)
        
        for price in (1, 2, 3):
            order = await self.auth_client.limit_order('buy', 'BTC-USD', 
                                                      price=price, size=1)
            await asyncio.sleep(0.5)
            
        for price in (20000, 30000, 40000):
            order = await self.auth_client.limit_order('sell', 'LTC-USD', 
                                                      price=price, size=0.01)
            await asyncio.sleep(0.5)    
        
        order = await self.auth_client.limit_order('buy', 'ETH-USD', 1, .01)

        order = await self.auth_client.market_order('sell', 'LTC-USD', .02,
                                                    stop='loss', stop_price=1)

        order = await self.auth_client.limit_order('buy', 'LTC-USD', 8000, .01,
                                                  stop='entry', stop_price=6500)

        order = await self.auth_client.market_order('buy', 'ETH-USD', .03,
                                                  stop='entry', stop_price=2000)
                                                    
        orders, _, _ = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(orders), 10)
        
        resp = await self.auth_client.cancel_all('BTC-USD')
        self.assertEqual(len(resp), 3)
        await asyncio.sleep(.5)
        orders, _, _ = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(orders), 7)
        
        resp = await self.auth_client.cancel_all()
        self.assertEqual(len(resp), 4)
        await asyncio.sleep(.5)
        orders, _, _ = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(orders), 3)
        
        resp = await self.auth_client.cancel_all(product_id='LTC-USD', stop=True)
        self.assertEqual(len(resp), 2)
        await asyncio.sleep(.5)
        orders, _, _ = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(orders), 1)
        
        resp = await self.auth_client.cancel_all(stop=True)
        self.assertEqual(len(resp), 1)
        await asyncio.sleep(.5)
        orders, _, _ = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(orders, [])        


    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_orders(self):
        # Assumes limit_order, market_order, and cancel_all work
        await self.auth_client.cancel_all(stop=True)
        orders, _, _, = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(orders), 0)
        
        open_ids = []
        for i in range(1, 4):
            price = 1 + i /10
            size = .001 * i
            order = await self.auth_client.limit_order('buy', 'BTC-USD', 
                                                      price=price, size=size)
            open_ids.append(order['id'])
            
        open_orders, _, _ = await self.auth_client.orders('open')
        self.assertEqual(len(open_orders), 3)
        self.assertEqual(open_orders[0]['id'], open_ids[2])
        self.assertEqual(open_orders[1]['id'], open_ids[1])
        self.assertEqual(open_orders[2]['id'], open_ids[0])
        
        active_ids = []
        for i in range(1,4):
            price = i + 1
            stop_price = i
            size = .01 * i
            order = await self.auth_client.limit_order('sell', 'LTC-USD',
                                             price=price, size=size,
                                             stop='loss', stop_price=stop_price)
            active_ids.append(order['id'])
            
        active_orders, _, _ = await self.auth_client.orders('active')
        self.assertEqual(len(active_orders), 3)
        self.assertEqual(active_orders[0]['id'], active_ids[2])
        self.assertEqual(active_orders[1]['id'], active_ids[1])
        self.assertEqual(active_orders[2]['id'], active_ids[0])
        
        market_ids = []
        for i in range(1,4):
            size = 0.001 * i
            order = await self.auth_client.market_order('buy', 'BTC-USD',
                                                        size=0.01)
            market_ids.append(order['id'])
            await asyncio.sleep(0.25)
            
        all_orders, _, _, = await self.auth_client.orders('all')
        self.assertGreaterEqual(len(all_orders), 9)
        self.assertEqual(all_orders[0]['id'], market_ids[2])
        self.assertEqual(all_orders[1]['id'], market_ids[1])
        self.assertEqual(all_orders[2]['id'], market_ids[0])
        self.assertEqual(all_orders[3]['id'], active_ids[2])
        
        oa_orders, _, _, = await self.auth_client.orders(['open', 'active'])
        self.assertGreaterEqual(len(all_orders), 9)
        self.assertEqual(oa_orders[0]['id'], active_ids[2])
        self.assertEqual(oa_orders[1]['id'], active_ids[1])
        self.assertEqual(oa_orders[2]['id'], active_ids[0])
        self.assertEqual(oa_orders[3]['id'], open_ids[2])
        self.assertEqual(oa_orders[4]['id'], open_ids[1])
        self.assertEqual(oa_orders[5]['id'], open_ids[0])
        
        oa_btc_orders, _, _  = await self.auth_client.orders(['open', 'active'],
                                                             'BTC-USD')
        self.assertEqual(oa_btc_orders[0]['id'], open_ids[2])
        self.assertEqual(oa_btc_orders[1]['id'], open_ids[1])
        self.assertEqual(oa_btc_orders[2]['id'], open_ids[0])
        
        orders, before, after = await self.auth_client.orders('all', limit=5)
        self.assertEqual(len(orders), 5)
        self.assertEqual(orders[0]['id'], market_ids[2])
        self.assertEqual(orders[4]['id'], active_ids[1])
        
        after_orders, after_before, after_after = await self.auth_client.orders(
                                                             'all', after=after)
        self.assertEqual(after_orders[0]['id'], active_ids[0])
        
        original_orders, _, _ = await self.auth_client.orders('all', before=after_before)
        self.assertEqual(original_orders, orders)
        
        await self.auth_client.cancel_all(stop=True)
        await asyncio.sleep(.5)
        oa_orders, _, _, = await self.auth_client.orders(['open', 'active'])
        self.assertEqual(len(oa_orders), 0)
        
        
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_get_order(self):
        # Assumes limit_order and market_order work
        ids = []
        for i in range(1, 4):
            price = 1 + i/10
            size = .001 * i
            order = await self.auth_client.limit_order('buy', 'BTC-USD', 
                                                      price=price, size=size)
            ids.append(order['id'])
            
        for i in range(1, 4):
            size = .001 * i
            order = await self.auth_client.market_order('sell', 'BTC-USD',
                                                        size=size)
            ids.append(order['id'])
            
        oid = random.choice(ids)
        order = await self.auth_client.get_order(oid)
        self.assertEqual(order['id'], oid)
        
        oid = random.choice(ids)
        order = await self.auth_client.get_order(oid)
        self.assertEqual(order['id'], oid)
        

        
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_fills(self):
        # Assumes market_order works
        
        orders = []
        for i in range(1, 5):
            btc_size = .001 * i
            ltc_size = .01 * i
            side = random.choice(['buy', 'sell'])
            
            order = await self.auth_client.market_order(side, 'BTC-USD', size=btc_size)
            orders.append(order)
            
            await asyncio.sleep(.25)
            
            order = await self.auth_client.market_order(side, 'LTC-USD', size=ltc_size)
            orders.append(order)
            
            await asyncio.sleep(.25)
            
        fills, _, _ = await self.auth_client.fills(product_id='BTC-USD')
        
        keys = {'created_at', 'fee', 'liquidity', 'order_id', 'price', 
                'product_id', 'profile_id', 'settled', 'side', 'size', 
                'trade_id', 'usd_volume', 'user_id'}
        self.assertGreaterEqual(len(fills), 4)
        self.assertEqual(fills[0]['order_id'], orders[6]['id'])
        
        fills, before, after = await self.auth_client.fills(product_id='LTC-USD', limit=3)
        self.assertEqual(len(fills), 3)
        self.assertEqual(fills[0]['order_id'], orders[7]['id'])
        
        after_fills, after_before, after_after = await self.auth_client.fills(
                                              product_id='LTC-USD', after=after)
                                              
        self.assertLess(after_fills[0]['trade_id'], fills[-1]['trade_id'])
        
        original_fills, _, _ = await self.auth_client.fills(product_id='LTC-USD',
                                                             before=after_before)
        self.assertEqual(original_fills, fills)
        
        order = random.choice(orders)
        fills, _, _ = await self.auth_client.fills(order_id=order['id'])
        self.assertGreaterEqual(len(fills), 1)
        
        total = 0
        for fill in fills:
            total += float(fill['size'])
        self.assertAlmostEqual(total, float(order['size']))
            
            
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_payment_methods(self):
        keys = {'id', 'type', 'name', 'currency', 'primary_buy', 'primary_sell',
                'allow_buy', 'allow_sell', 'allow_deposit', 'allow_withdraw',
                'limits'}

        methods = await self.auth_client.payment_methods()
        self.assertIsInstance(methods, list)
        self.assertIsInstance(methods[0], dict)
        self.assertGreaterEqual(methods[0].keys(), keys)
        

    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_coinbase_accounts(self):
        keys =  {'id', 'name', 'balance', 'currency', 'type', 'primary', 'active'}
        
        accounts = await self.auth_client.coinbase_accounts()
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], dict)
        self.assertGreaterEqual(accounts[0].keys(), keys)
        
        
    @expectedFailure
    @skipUnless(TEST_AUTH and TEST_USD_ACCOUNT and TEST_USD_PAYMENT_METHOD,
    "Auth credentials, test USD account, and test USD payment method required.")
    async def test_deposit_payment_method(self):
        # As of 11/25/18 this call returns a 401 error:
        # "refresh of oauth token failed"
        resp = await self.auth_client.deposit_payment_method(1500, 'USD', 
                                                        TEST_USD_PAYMENT_METHOD)
                                                        
        keys = {'amount', 'currency', 'id', 'payout_at'}
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp.keys(), keys)
        self.assertEqual(float(resp['amount']), 1500.0)
        self.assertEqual(resp['currency'], 'USD')
    

    @skipUnless(TEST_AUTH and TEST_USD_ACCOUNT and TEST_USD_COINBASE_ACCOUNT, 
    "Auth credentials, test USD account, and test usd Coinbase account  required")
    async def test_deposit_cointbase(self):
        
        resp = await self.auth_client.deposit_coinbase(150, 'USD',
                                                      TEST_USD_COINBASE_ACCOUNT)
        
        keys = {'amount', 'currency', 'id'}
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp.keys(), keys)
        self.assertEqual(resp['currency'], 'USD')
        self.assertEqual(float(resp['amount']), 150.0)

    @expectedFailure
    @skipUnless(TEST_AUTH and TEST_USD_ACCOUNT and TEST_USD_PAYMENT_METHOD,
    "Auth credentials, test USD account, and test USD payment method required.")
    async def test_withdraw_payment_method(self):
        # As of 11/25/18 this call returns a 401 error:
        # "refresh of oauth token failed"    
        resp = await self.auth_client.withdraw_payment_method(1500, 'USD', 
                                                        TEST_USD_PAYMENT_METHOD)
                                                        
        keys = {'amount', 'currency', 'id', 'payout_at'}
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp.keys(), keys)
        self.assertEqual(float(resp['amount']), 1500.0)
        self.assertEqual(resp['currency'], 'USD')        
        

    @skipUnless(TEST_AUTH and TEST_USD_ACCOUNT and TEST_USD_COINBASE_ACCOUNT, 
    "Auth credentials, test USD account, and test usd Coinbase account  required")
    async def test_withdraw_cointbase(self):

        resp = await self.auth_client.withdraw_coinbase(75, 'USD',
                                                      TEST_USD_COINBASE_ACCOUNT)
        
        keys = {'amount', 'currency', 'id'}
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp.keys(), keys)
        self.assertEqual(resp['currency'], 'USD')
        self.assertEqual(float(resp['amount']), 75.0)


    @expectedFailure
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_withdraw_crypto(self):
        # As of 11/25/18 this call returns a 401 error:
        # "refresh of oauth token failed - The funds were transferred to 
        # Coinbase for processing, but failed to withdraw to 
        # 0x5ad5769cd04681FeD900BCE3DDc877B50E83d469. Please manually withdraw 
        # from Coinbase."
        address = "0x5ad5769cd04681FeD900BCE3DDc877B50E83d469"
        
        resp = await self.auth_client.withdraw_crypto(.001, 'LTC', address)

      
    @expectedFailure 
    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_stablecoin_conversion(self):
        # As of 11/25/18 this call returns a 400 error:
        # "USDC is not enabled for your account"
        resp = await self.auth_client.stablecoin_conversion('USD', 'USDC', 100)
        
        keys = {'amount', 'id', 'from', 'from_account_id', 'to', 'to_account_id'}
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp.keys(), keys)
        self.assertEqual(float(resp['amount']), 100.0)
        self.assertEqual(resp['from'], 'USD')
        self.assertEqual(resp['to'], 'USDC')
        
    @expectedFailure
    @skipUnless(TEST_AUTH, "AUTH credentials required")
    async def test_fees(self):
        #As of 10/15/19, the Sandbox server returns a 500 error:
        #"Internal server error"
        keys = {'maker_fee_rate', 'taker_fee_rate', 'usd_volume'}
        
        fees  = await self.auth_client.fees()
        self.assertIsInstance(tick, dict)
        self.assertEqual(tick.keys(), keys)        


    @skipUnless(TEST_AUTH and TEST_BTC_ACCOUNT, "Auth credentials and test BTC account ID required")
    async def test_reports(self):
        # Combines tests for create_report and report_status
        orders = []
        for i in range(1, 4):
            size = .001 * i
            side = random.choice(['buy', 'sell'])
            
            order = await self.auth_client.market_order(side, 'BTC-USD', size=size)
            orders.append(order)
            await asyncio.sleep(.25)
        
        keys = {'id', 'type', 'status'}
        
        end = datetime.utcnow()
        start = end - timedelta(days=1)
        end = end.isoformat()
        start = start.isoformat()
        resp1 = await self.auth_client.create_report('account', start, end,
                                                    account_id=TEST_BTC_ACCOUNT)
        self.assertIsInstance(resp1, dict)
        self.assertEqual(resp1.keys(), keys)
        self.assertEqual(resp1['type'], 'account')
        
        resp2 = await self.auth_client.create_report('fills', start, end,
                                                          product_id='BTC-USD')
        self.assertIsInstance(resp2, dict)
        self.assertEqual(resp2.keys(), keys)
        self.assertEqual(resp2['type'], 'fills')
        
        resp3 = await self.auth_client.create_report('fills', start, end,
                                      product_id='BTC-USD', report_format='csv', 
                                      email='test@example.com')
                                      
        self.assertIsInstance(resp3, dict)
        self.assertEqual(resp3.keys(), keys)
        self.assertEqual(resp3['type'], 'fills')
        
        await asyncio.sleep(10)
        
        status1 = await self.auth_client.report_status(resp1['id'])
        
        keys = {'completed_at', 'created_at', 'expires_at', 'file_url', 'id', 
                'params', 'status', 'type', 'user_id'}
        statuses = {'pending', 'creating', 'ready'}
        self.assertIsInstance(status1, dict)
        self.assertEqual(status1.keys(), keys)
        self.assertEqual(status1['id'], resp1['id'])
        self.assertEqual(status1['type'], 'account')
        self.assertIn(status1['status'], statuses)
        self.assertEqual(status1['params']['start_date'], start)
        self.assertEqual(status1['params']['end_date'], end)
        self.assertEqual(status1['params']['format'], 'pdf')
        self.assertEqual(status1['params']['account_id'], TEST_BTC_ACCOUNT)
        
        status2 = await self.auth_client.report_status(resp2['id'])
        self.assertIsInstance(status2, dict)
        self.assertEqual(status2.keys(), keys)
        self.assertEqual(status2['id'], resp2['id'])
        self.assertEqual(status2['type'], 'fills')
        self.assertIn(status2['status'], statuses)
        self.assertEqual(status2['params']['start_date'], start)
        self.assertEqual(status2['params']['end_date'], end)
        self.assertEqual(status2['params']['format'], 'pdf')
        self.assertEqual(status2['params']['product_id'], 'BTC-USD')
        
        status3 = await self.auth_client.report_status(resp3['id'])
        self.assertIsInstance(status3, dict)
        self.assertEqual(status3.keys(), keys)
        self.assertEqual(status3['id'], resp3['id'])
        self.assertEqual(status3['type'], 'fills')
        self.assertIn(status3['status'], statuses)
        self.assertEqual(status3['params']['start_date'], start)
        self.assertEqual(status3['params']['end_date'], end)
        self.assertEqual(status3['params']['email'], 'test@example.com')
        self.assertEqual(status3['params']['format'], 'csv')


    @skipUnless(TEST_AUTH, "Auth credentials required")
    async def test_trailing_volume (self):
        tv = await self.auth_client.trailing_volume()
        
        keys ={'product_id', 'volume', 'exchange_volume', 'recorded_at'}
        self.assertIsInstance(tv, list)
        self.assertIsInstance(tv[0], dict)
        self.assertEqual(tv[0].keys(), keys)
