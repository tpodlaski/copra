#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.Client` class.
"""

import asyncio
from datetime import datetime, timedelta
import json
import time
import urllib.parse

import aiohttp
from asynctest import CoroutineMock
from multidict import MultiDict

from copra.rest import APIRequestError, Client, URL
from copra.rest.client import HEADERS
from tests.unit.rest.util import MockTestCase

# These are made up
TEST_KEY = 'a035b37f42394a6d343231f7f772b99d'
TEST_SECRET = 'aVGe54dHHYUSudB3sJdcQx4BfQ6K5oVdcYv4eRtDN6fBHEQf5Go6BACew4G0iFjfLKJHmWY5ZEwlqxdslop4CC=='
TEST_PASSPHRASE = 'a2f9ee4dx2b'

UNAUTH_HEADERS = HEADERS

AUTH_HEADERS = HEADERS.copy()

AUTH_HEADERS.update({
                      'Content-Type': 'Application/JSON',
                      'CB-ACCESS-TIMESTAMP': '*',
                      'CB-ACCESS-SIGN': '*',
                      'CB-ACCESS-KEY': TEST_KEY,
                      'CB-ACCESS-PASSPHRASE': TEST_PASSPHRASE
                    })


class TestRest(MockTestCase):
    """Tests for copra.rest.Client"""

    def setUp(self):
        super().setUp()
        self.client = Client(self.loop)
        self.auth_client = Client(self.loop, auth=True, key=TEST_KEY, 
                                  secret=TEST_SECRET, passphrase=TEST_PASSPHRASE)       
    
    
    def tearDown(self):
        self.loop.create_task(self.client.close())
        self.loop.create_task(self.auth_client.close())


    async def test__init__(self):
        # No loop
        with self.assertRaises(TypeError):
            client = Client()
        
        self.assertEqual(self.client.loop, self.loop)
        self.assertEqual(self.client.url, URL)
        self.assertFalse(self.client.auth)
        self.assertIsInstance(self.client.session, aiohttp.ClientSession)
        self.assertFalse(self.client.session.closed)

        client = Client(self.loop, 'http://www.example.com')
        self.assertEqual(client.url,'http://www.example.com')
        await client.session.close()
            
        #auth, no key, secret, or passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, auth=True)
        
        #auth, key, no secret or passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, auth=True, key='MyKey')
        
        #auth, key, secret, no passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, auth=True, key='MyKey', secret='MySecret')
                        
        #auth, secret, no key or passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, auth=True, secret='MySecret')
        
        #auth, secret, passphrase, no key
        with self.assertRaises(ValueError):
            client = Client(self.loop, auth=True, secret='MySecret',
                            passphrase='MyPassphrase')
                            
        #auth, passphrase, no key or secret
        with self.assertRaises(ValueError):
            client = Client(self.loop, auth=True, passphrase='MyPassphrase')
                        
        #auth, key, secret, passphrase
        self.assertTrue(self.auth_client.auth)
        self.assertEqual(self.auth_client.key, TEST_KEY)
        self.assertEqual(self.auth_client.secret, TEST_SECRET)
        self.assertEqual(self.auth_client.passphrase, TEST_PASSPHRASE)
        
        
    async def test_close(self):
        client = Client(self.loop)
        self.assertFalse(client.session.closed)
        self.assertFalse(client.closed)
        await client.close()
        self.assertTrue(client.session.closed)
        self.assertTrue(client.closed)
        
        
    async def test_context_manager(self):
        async with Client(self.loop) as client:
            self.assertFalse(client.closed)
        self.assertTrue(client.closed)
    
        try:
            async with Client(self.loop) as client:
                raise ValueError()
        except ValueError:
            pass
        self.assertTrue(client.closed)


    async def test__get_auth_headers(self):
        
        async with Client(self.loop) as client:
            with self.assertRaises(ValueError):
                client._get_auth_headers('/mypath')
                    
        path = '/mypath'
        timestamp = 1539968909.917318
        
        # Default GET
        headers = self.auth_client._get_auth_headers(path, timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'haapGobLuJMel4ku5s7ptzyNkQdYtLPMXgQJq5f1/cg=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)
        
        # Explicit GET
        headers = self.auth_client._get_auth_headers(path, method='GET', timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'haapGobLuJMel4ku5s7ptzyNkQdYtLPMXgQJq5f1/cg=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)
        
        # POST
        headers = self.auth_client._get_auth_headers(path, method='POST', timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'Geo8uJefQp5CG42SYsmKW1lvR7t+28ujcgt3yRM1mpA=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)

        # DELETE
        headers = self.auth_client._get_auth_headers(path, method='DELETE', timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'NRdGfZaOAkFK2ENVDJQ43Rg+fLm+6vg4PML/yzmtuiY=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)
        
    
    async def test__handle_error(self):
        self.mock_get.return_value.status = 404
        self.mock_get.return_value.json.return_value = {'message': 'ERROR MESSAGE'}
        
        with self.assertRaises(APIRequestError) as cm:
            headers, body = await self.client.get('http://www.example.com/fail')
        
        err = cm.exception  
        self.assertEqual(err.__str__(), 'ERROR MESSAGE [404]')
        self.assertEqual(err.response, self.mock_get.return_value)
        
    
    async def test_delete(self):
        path = '/mypath'
        query = {'key1': 'item1', 'key2': 'item2'}

        # Unauthorized call by unauthorized client
        resp = await self.client.delete(path, query)
        self.check_req(self.mock_del, '{}{}'.format(URL, path), query=query, headers=UNAUTH_HEADERS)
        
        # Unauthorized call by unauthorized client, no query
        resp = await self.client.delete(path)
        self.check_req(self.mock_del, '{}{}'.format(URL, path), query={}, headers=UNAUTH_HEADERS)
       
        # Authorized call by unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.delete(path, query, auth=True)
            
        # Unauthorized call by authorized client
        resp = await self.auth_client.delete(path, query)
        self.check_req(self.mock_del, '{}{}'.format(URL, path), query=query, headers=UNAUTH_HEADERS)
        
        # Authorized call by authorized client
        resp = await self.auth_client.delete(path, query, auth=True)
        self.check_req(self.mock_del, '{}{}'.format(URL, path), query=query, headers=AUTH_HEADERS)
        
        qs = '?{}'.format(urllib.parse.urlencode(query))
        expected_headers = self.auth_client._get_auth_headers(path + qs, 'DELETE', timestamp=self.mock_del.headers['CB-ACCESS-TIMESTAMP'])
        self.assertEqual(self.mock_del.headers['CB-ACCESS-SIGN'], expected_headers['CB-ACCESS-SIGN'])
        
    
    async def test_get(self):
        path = '/mypath'
        query = {'key1': 'item1', 'key2': 'item2'}
        
        # Unauthorized call by unauthorized client
        resp = await self.client.get(path, query)
        self.check_req(self.mock_get, '{}{}'.format(URL, path), query=query, headers=UNAUTH_HEADERS)
        
        # Unauthorized call by unauthorized client, no query
        resp = await self.client.get(path)
        self.check_req(self.mock_get, '{}{}'.format(URL, path), query={}, headers=UNAUTH_HEADERS)
        
        # Authorized call by unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.get(path, query, auth=True)
            
        # Unauthorized call by authorized client
        resp = await self.auth_client.get(path, query)
        self.check_req(self.mock_get, '{}{}'.format(URL, path), query=query, headers=UNAUTH_HEADERS)
        
        # Authorized call by authorized client
        resp = await self.auth_client.get(path, query, auth=True)
        self.check_req(self.mock_get, '{}{}'.format(URL, path), query=query, headers=AUTH_HEADERS)
        
        qs = '?{}'.format(urllib.parse.urlencode(query))
        expected_headers = self.auth_client._get_auth_headers(path + qs, 'GET', timestamp=self.mock_get.headers['CB-ACCESS-TIMESTAMP'])
        self.assertEqual(self.mock_get.headers['CB-ACCESS-SIGN'], expected_headers['CB-ACCESS-SIGN'])


    async def test_post(self):
        path = '/mypath'
        data = {'key1': 'item1', 'key2': 'item2'}
        
        # Unauthorized call by unauthorized client
        resp = await self.client.post(path, data)
        self.check_req(self.mock_post, '{}{}'.format(URL, path), data=data, headers=UNAUTH_HEADERS)
        
        # Unauthorized call by unauthorized client, no data
        resp = await self.client.post(path)
        self.check_req(self.mock_post, '{}{}'.format(URL, path), data={}, headers=UNAUTH_HEADERS)
        
        # Authorized call by unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.post(path, data, auth=True)
            
        # Unauthorized call by authorized client
        resp = await self.auth_client.post(path, data)
        self.check_req(self.mock_post, '{}{}'.format(URL, path), data=data, headers=UNAUTH_HEADERS)
        
        # Authorized call by authorized client
        resp = await self.auth_client.post(path, data, auth=True)
        self.check_req(self.mock_post, '{}{}'.format(URL, path), data=data, headers=AUTH_HEADERS)
        
        data = json.dumps(data)
        expected_headers = self.auth_client._get_auth_headers(path, 'POST', data=data, timestamp=self.mock_post.headers['CB-ACCESS-TIMESTAMP'])
        self.assertEqual(self.mock_post.headers['CB-ACCESS-SIGN'], expected_headers['CB-ACCESS-SIGN'])
        

    async def test_products(self):
        
        products = await self.client.products()
        self.check_req(self.mock_get, '{}{}'.format(URL, '/products'), headers=UNAUTH_HEADERS)
            

    async def test_order_book(self):            

        with self.assertRaises(TypeError):
            ob = await self.client.order_book()
            
        with self.assertRaises(ValueError):
            ob = await self.client.order_book('BTC-USD', 99)
            
        # Default level 1
        ob = await self.client.order_book('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/book'.format(URL), 
                      query={'level': '1'}, headers=UNAUTH_HEADERS)
        
        # Level 1
        ob = await self.client.order_book('BTC-USD', level=1)
        self.check_req(self.mock_get, '{}/products/BTC-USD/book'.format(URL), 
                      query={'level': '1'}, headers=UNAUTH_HEADERS)
        
        # Level 2
        ob = await self.client.order_book('BTC-USD', level=2)
        self.check_req(self.mock_get, '{}/products/BTC-USD/book'.format(URL), 
                      query={'level': '2'}, headers=UNAUTH_HEADERS)

        # Level 3
        ob = await self.client.order_book('BTC-USD', level=3)
        self.check_req(self.mock_get, '{}/products/BTC-USD/book'.format(URL), 
                      query={'level': '3'}, headers=UNAUTH_HEADERS)


    async def test_ticker(self):
        
        # No product_id
        with self.assertRaises(TypeError):
            tick = await self.client.ticker()
            
        tick = await self.client.ticker('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/ticker'.format(URL), 
                      headers=UNAUTH_HEADERS)


    async def test_trades(self):
        
        # No product_id
        with self.assertRaises(TypeError):
            trades, before, after = await self.client.trades()
            
        # before and after
        with self.assertRaises(ValueError):
            trades, before, after = await self.client.trades('BTC-USD', before=1, after=100)
            
        trades, before, after = await self.client.trades('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/trades'.format(URL),
                      query={'limit': '100'}, headers=UNAUTH_HEADERS)
        
        ret_headers = {'cb-before': '51590012', 'cb-after': '51590010'}
        body = [{'trade_id': 1}, {'trade_id': 2}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
            
        trades, before, after = await self.client.trades('BTC-USD', limit=5)
        self.check_req(self.mock_get, '{}/products/BTC-USD/trades'.format(URL),
                      query={'limit': '5'}, headers=UNAUTH_HEADERS)        
        self.assertEqual(trades, body)
        self.assertEqual(before, ret_headers['cb-before'])
        self.assertEqual(after, ret_headers['cb-after'])
            
        prev_trades, prev_before, prev_after = await self.client.trades('BTC-USD', before=before)
        self.check_req(self.mock_get, '{}/products/BTC-USD/trades'.format(URL),
                      query={'limit': '100', 'before': before}, headers=UNAUTH_HEADERS) 
        
        next_trades, next_before, next_after = await self.client.trades('BTC-USD', after=after)
        self.check_req(self.mock_get, '{}/products/BTC-USD/trades'.format(URL),
                      query={'limit': '100', 'after': after}, headers=UNAUTH_HEADERS) 


    async def test_historic_rates(self):
        
        # No product_id
        with self.assertRaises(TypeError):
            rates = await self.client.historic_rates()
            
        # Invalid granularity
        with self.assertRaises(ValueError):
            rates = await self.client.historic_rates('BTC-USD', granularity=100)
        
        end = datetime.utcnow()
        start = end - timedelta(days=1)
        
        # start, no end
        with self.assertRaises(ValueError):
            rates = await self.client.historic_rates('BTC-USD', start=start)
            
        #end, no start
        with self.assertRaises(ValueError):
            rates = await self.client.historic_rates('BTC-USD', end=end)
            
        # Default granularity
        rates = await self.client.historic_rates('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/candles'.format(URL),
                      query={'granularity': '3600'}, headers=UNAUTH_HEADERS)

        # Custom granularity, start, end
        rates = await self.client.historic_rates('BTC-USD', 900, 
                                                 start.isoformat(), 
                                                 end.isoformat())
        self.check_req(self.mock_get, '{}/products/BTC-USD/candles'.format(URL),
                      query={'granularity': '900', 'start': start.isoformat(),
                              'end': end.isoformat()},
                      headers=UNAUTH_HEADERS)
                       
    async def test_get_24hour_stats(self):
        
        # No product_id
        with self.assertRaises(TypeError):
            stats = await self.client.get_24hour_stats()

        stats = await self.client.get_24hour_stats('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/stats'.format(URL), headers=UNAUTH_HEADERS)


    async def test_currencies(self):

        currencies = await self.client.currencies()
        self.check_req(self.mock_get, '{}/currencies'.format(URL), headers=UNAUTH_HEADERS)

        
    async def test_server_time(self):
        
        time = await self.client.server_time()
        self.check_req(self.mock_get, '{}/time'.format(URL), headers=UNAUTH_HEADERS)


    async def test_accounts(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            accounts = await self.client.accounts()        
        
        accounts = await self.auth_client.accounts()
        self.check_req(self.mock_get, '{}/accounts'.format(URL), headers=AUTH_HEADERS)
  

    async def test_account(self):

        # No account_id
        with self.assertRaises(TypeError):
            trades, before, after = await self.auth_client.account()        

        # Unauthorized client
        with self.assertRaises(ValueError):
            acount = await self.client.account(42)
            
        account = await self.auth_client.account(42)
        self.check_req(self.mock_get, '{}/accounts/42'.format(URL), headers=AUTH_HEADERS)


    async def test_account_history(self):

        # No account_id
        with self.assertRaises(TypeError):
            trades, before, after = await self.auth_client.account_history()
        
        # Unauthorized client        
        with self.assertRaises(ValueError):
            trades, before, after = await self.client.account_history(42)
        
        # before and after both set
        with self.assertRaises(ValueError):
            trades, before, after = await self.auth_client.account_history(42, 
                                                before='earlier', after='later')
            
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}
        body = [{'id': '1'}, {'id': '2'}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body

        trades, before, after = await self.auth_client.account_history(42, limit=5)
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(trades, body)
        self.check_req(self.mock_get, '{}/accounts/42/ledger'.format(URL), 
                      query={'limit': '5'}, headers=AUTH_HEADERS)
        
        
        trades, before, after = await self.auth_client.account_history(42, before=before)
        self.check_req(self.mock_get, '{}/accounts/42/ledger'.format(URL), 
                      query={'limit': '100', 'before': before}, headers=AUTH_HEADERS)
        
        trades, before, after = await self.auth_client.account_history(42, after=after)
        self.check_req(self.mock_get, '{}/accounts/42/ledger'.format(URL), 
                      query={'limit': '100', 'after': after}, headers=AUTH_HEADERS)
 

    async def test_holds(self):
        
        # No account_id
        with self.assertRaises(TypeError):
            holds, before, after = await self.auth_client.holds()
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            holds, before, after = await self.client.holds(42)
            
        # before and after both set
        with self.assertRaises(ValueError):
            holds, before, after = await self.auth_client.holds(42, 
                                              before='earlier', after='later')
            
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}
        body = [{'id': '1'}, {'id': '2'}]

        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
                
        holds, before, after = await self.auth_client.holds(42, limit=5)
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(holds, body)
        self.check_req(self.mock_get, '{}/accounts/42/holds'.format(URL), 
                      query={'limit': '5'}, headers=AUTH_HEADERS)
        
        holds, before, after = await self.auth_client.holds(42, before=before)
        self.check_req(self.mock_get, '{}/accounts/42/holds'.format(URL), 
                      query={'limit': '100', 'before': before}, headers=AUTH_HEADERS)                                                    
        
        holds, before, after = await self.auth_client.holds(42, after=after)
        self.check_req(self.mock_get, '{}/accounts/42/holds'.format(URL), 
                      query={'limit': '100', 'after': after}, headers=AUTH_HEADERS)


    async def test_limit_order(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.limit_order('buy', 'BTC-USD', 1, 100)          
        
        # Invalid side
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('right', 'BTC-USD', 1, 100)
        
        # Invalid time_in_force
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 100, 5,
                                                      time_in_force='OPP')
                                                      
        # GTT time_in_force, no cancel_after
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC_USD', 2, 60,
                                                      time_in_force='GTT')
                                                      
        # Invalid cancel_after
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 3, 47,
                                                      time_in_force='GTT',
                                                      cancel_after='lifetime')
                                                      
        # cancel_after wrong time_in_force
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 4, 33,
                                                      time_in_force='FOK',
                                                      cancel_after='hour')

        # IOC time_in_force, post_only True
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 5, 82,
                                                      time_in_force='IOC',
                                                      post_only=True)
                                                      
        # FOK time_in_force, post_only True
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 6, 12,
                                                      time_in_force='FOK',
                                                      post_only=True)
                                                      
        # Invalid stp
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 7, 14,
                                                      stp='Core')

        # Default order_type, time_in_force
        resp = await self.auth_client.limit_order('buy', 'BTC-USD', 1.1, 3.14)
        
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                            'type': 'limit', 'price': 1.1,
                            'size': 3.14, 'time_in_force': 'GTC', 
                            'post_only': False, 'stp': 'dc'},
                      headers=AUTH_HEADERS)
                      
        # GTT order with cancel_after
        resp = await self.auth_client.limit_order('buy', 'BTC-USD', 1.7, 29,
                            time_in_force='GTT', cancel_after='hour')
                            
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                            'type': 'limit', 'price': 1.7, 'size': 29, 
                            'time_in_force': 'GTT', 'cancel_after': 'hour',
                            'post_only': False, 'stp': 'dc'},
                        headers=AUTH_HEADERS)
                        
        # client_oid, stp
        resp = await self.auth_client.limit_order('buy', 'LTC-USD', 0.8, 11,
                            client_oid='back', stp='cb')        

        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'LTC-USD',
                            'type': 'limit', 'price': 0.8, 'size': 11, 
                            'time_in_force': 'GTC', 'client_oid': 'back',
                            'post_only': False, 'stp': 'cb'},
                        headers=AUTH_HEADERS)        


    async def test_limit_order_stop(self):
        
        # Invalid stop
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 1, .001, 
                                              stop="Hammer Time", stop_price=10)
        # stop w/ no stop_price
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 1, .001, 
                                                      stop="loss")
                                            
        # stop_price w/ no stop
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'BTC-USD', 2, .002,
                                                      stop_price=10)
                                                       
        # stop w/ post_only True
        with self.assertRaises(ValueError):
            resp = await self.auth_client.limit_order('buy', 'LTC-USD', 3, .003,
                                 stop='entry', stop_price=10000, post_only=True)
        
        # stop loss
        resp = await self.auth_client.limit_order('sell', 'BTC-USD', 3.5, .004,
                                                  stop='loss', stop_price=4)
        
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'sell', 'product_id': 'BTC-USD',
                            'type': 'limit', 'price': 3.5,
                            'size': .004, 'time_in_force': 'GTC', 
                            'post_only': False, 'stp': 'dc', 'stop': 'loss',
                            'stop_price': 4},
                      headers=AUTH_HEADERS)
                      
        # stop entry
        resp = await self.auth_client.limit_order('buy', 'BTC-USD', 10000, .005,
                                                 stop='entry', stop_price=11000)
        
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                            'type': 'limit', 'price': 10000,
                            'size': .005, 'time_in_force': 'GTC', 
                            'post_only': False, 'stp': 'dc', 'stop': 'entry',
                            'stop_price': 11000},
                      headers=AUTH_HEADERS)

    
    async def test_market_order(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.market_order('buy', 'BTC-USD', .001)
        
        # Invalid side
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('dark', 'BTC-USD', .001)
            
        # No funds or size
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('buy', 'BTC-USD')
            
        # funds and size
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('buy', 'BTC-USD',
                                              size=.001, funds=10000)
                                               
        # Invalid stp
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('buy', 'BTC-USD', 
                                                      size=.001, stp='plush')

        # Size, no client_oid, default stp
        resp = await self.auth_client.market_order('buy', 'BTC-USD', size=5)
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                            'type': 'market', 'size': 5, 'stp': 'dc'},
                      headers=AUTH_HEADERS)

        # Size, client_oid, stp
        resp = await self.auth_client.market_order('buy', 'BTC-USD', size=3,
                                                client_oid='Order 66', stp='co')
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                          'type': 'market', 'size': 3, 'client_oid': 'Order 66', 
                          'stp': 'co'},
                      headers=AUTH_HEADERS)
                      
        # Funds, no client_oid, default stp
        resp = await self.auth_client.market_order('buy', 'BTC-USD', funds=500)
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                            'type': 'market', 'funds': 500, 'stp': 'dc'},
                      headers=AUTH_HEADERS)

        # Funds, client_oid, stp
        resp = await self.auth_client.market_order('buy', 'BTC-USD', funds=300,
                                             client_oid='of the Jedi', stp='cb')
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                          'type': 'market', 'funds': 300, 
                          'client_oid': 'of the Jedi', 'stp': 'cb'},
                      headers=AUTH_HEADERS)


    async def test_market_order_stop(self):
        
        # Invalid stop
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('buy', 'BTC-USD', .001,
                                            stop="Hammer Time", stop_price=10)
                                                       
        # stop w/ no stop_price
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('buy', 'BTC-USD', .001,
                                                      stop="loss")
                                            
        # stop_price w/ no stop
        with self.assertRaises(ValueError):
            resp = await self.auth_client.market_order('buy', 'BTC-USD', .001,
                                                      stop_price=10)
                                                      
        # stop loss
        resp = await self.auth_client.market_order('sell', 'BTC-USD', size=.002,
                                                    stop='loss', stop_price=2.2)
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'sell', 'product_id': 'BTC-USD',
                            'type': 'market', 'size': .002, 'stp': 'dc',
                            'stop': 'loss', 'stop_price': 2.2},
                      headers=AUTH_HEADERS)
                      
        # stop entry
        resp = await self.auth_client.market_order('buy', 'BTC-USD', size=.003,
                                                  stop='entry', stop_price=9000)
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                      data={'side': 'buy', 'product_id': 'BTC-USD',
                            'type': 'market', 'size': .003, 'stp': 'dc',
                            'stop': 'entry', 'stop_price': 9000},
                      headers=AUTH_HEADERS)       
                                                       

    async def test_cancel(self):
        
        with self.assertRaises(TypeError):
            resp = await self.auth_client.cancel()
            
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.cancel(42)
            
        resp = await self.auth_client.cancel(42)
        self.check_req(self.mock_del, '{}/orders/42'.format(URL), headers=AUTH_HEADERS)

        
    async def test_cancel_all(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.cancel_all()
            
        # No product_idx
        resp = await self.auth_client.cancel_all()
        self.check_req(self.mock_del, '{}/orders'.format(URL), headers=AUTH_HEADERS)
        
        # product_id
        resp = await self.auth_client.cancel_all('BTC-USD')
        self.check_req(self.mock_del, '{}/orders'.format(URL), 
                      query={'product_id': 'BTC-USD'}, headers=AUTH_HEADERS)


    async def test_orders(self):
        
        # Unauthorizerd client
        with self.assertRaises(ValueError):
            orders, before, after = await self.client.orders()
            
        # before and after both set
        with self.assertRaises(ValueError):
            orders, before, after = await self.auth_client.orders(
                                      before='nighttime', after='morning')
        
        # Invalid status string
        with self.assertRaises(ValueError):
            orders, before, after = await self.auth_client.orders('fresh')
            
        # Invalid status string in list
        with self.assertRaises(ValueError):
            orders, before, after = await self.auth_client.orders(['open', 'stale', 'pending'])
            
        # Default status, default product_id, default limit
        orders, before, after = await self.auth_client.orders()
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'limit': '100'}, headers=AUTH_HEADERS)
        
        # String status, default product_id, default limit
        orders, before, after = await self.auth_client.orders('open')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'limit': '100', 'status': 'open'}, headers=AUTH_HEADERS)
        
        # List status, default product_id, default limit
        orders, before, after = await self.auth_client.orders(['pending', 'open'])
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query=MultiDict([('limit', '100'), ('status', 'pending'), ('status', 'open')]),
                      headers=AUTH_HEADERS)        
        
        # product_id, default status, default limit
        orders, before, after = await self.auth_client.orders(product_id='BTC-USD')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'product_id': 'BTC-USD', 'limit': '100'},
                      headers=AUTH_HEADERS)
                       
        # product_id, string status, default limit
        orders, before, after = await self.auth_client.orders('open', 'BTC-USD')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '100'},
                      headers=AUTH_HEADERS)
                       
        # product_id, list status, default limit
        orders, before, after = await self.auth_client.orders(['pending', 'active'], 'BTC-USD')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query=MultiDict([('status', 'pending'), ('status', 'active'), ('product_id','BTC-USD'), ('limit', '100')]),
                      headers=AUTH_HEADERS)
                      
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}

        body = [{'order_id': '1'}, {'order_id': '2'}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
        
        # product_id, list_status, custom limit
        orders, before, after = await self.auth_client.orders('open', 'BTC-USD', limit=5)
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(orders, body)
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '5'},
                      headers=AUTH_HEADERS)
                       
        orders, before, after = await self.auth_client.orders('open', 'BTC-USD', before=before)
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '100', 'before': before},
                      headers=AUTH_HEADERS)
                       
        orders, before, after = await self.auth_client.orders('open', 'BTC-USD', after=after)
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '100', 'after': after},
                      headers=AUTH_HEADERS)
                       
                       
    async def test_get_order(self):
        
        # Unauthorizerd client
        with self.assertRaises(ValueError):
            order = await self.client.get_order(42)
            
        # No order_id
        with self.assertRaises(TypeError):
            order = await self.auth_client.get_order()
            
        # order_id
        order = await self.auth_client.get_order(42)
        self.check_req(self.mock_get, '{}/orders/42'.format(URL), headers=AUTH_HEADERS)
        
        
    async def test_fills(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            fills, before, after = await self.client.fills()
            
        # before and after both set
        with self.assertRaises(ValueError):
            fills, before, after = await self.auth_client.fills('33', 
                                                      before='BC', after='AD')
            
        # order_id and product_id not defined
        with self.assertRaises(ValueError):
            fills, before, after = await self.auth_client.fills()
            
        # order_id and product_id both defined
        with self.assertRaises(ValueError):
            fills, before, after = await self.auth_client.fills('42', 'BTC-USD')
        
        # order_id
        fills, before, after = await self.auth_client.fills('42')
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                      query={'order_id': '42', 'limit': '100'}, headers=AUTH_HEADERS)
                       
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}

        body = [{'trade_id': '1'}, {'trade_id': '2'}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
        
        # product_id
        fills, before, after = await self.auth_client.fills(product_id='BTC-USD')
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                      query={'product_id': 'BTC-USD', 'limit': '100'}, headers=AUTH_HEADERS)  
        
        # limit, before cursor
        fills, before, after = await self.auth_client.fills('42', limit=5, before=before)
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                      query={'order_id': '42', 'limit': '5', 'before': before}, 
                      headers=AUTH_HEADERS)
                       
        # after cursor
        fills, before, after = await self.auth_client.fills('42', after=after)
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                      query={'order_id': '42', 'limit': '100', 'after': after}, 
                      headers=AUTH_HEADERS)
                       

    async def test_payment_methods(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            methods = await self.client.payment_methods()
            
        methods = await self.auth_client.payment_methods()
        self.check_req(self.mock_get, '{}/payment-methods'.format(URL), headers=AUTH_HEADERS)
        
        
    async def test_coinbase_accounts(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            accounts = await self.client.coinbase_accounts()
            
        accounts = await self.auth_client.coinbase_accounts()
        self.check_req(self.mock_get, '{}/coinbase-accounts'.format(URL), headers=AUTH_HEADERS)
        
        
    async def test_deposit_payment_method(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.deposit_payment_method(3.14, 'EUR', '10')
            
        resp =await self.auth_client.deposit_payment_method(1000, 'USD', '42')
        self.check_req(self.mock_post, '{}/deposits/payment-method'.format(URL),
                      data={'amount': 1000, 'currency': 'USD', 
                             'payment_method_id': '42'}, 
                        headers=AUTH_HEADERS)
                        
                        
    async def test_deposit_coinbase(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.deposit_coinbase(1000, 'BTC', '7')
            
        resp =await self.auth_client.deposit_coinbase(95, 'LTC', 'A1')
        self.check_req(self.mock_post, '{}/deposits/coinbase-account'.format(URL),
                      data={'amount': 95, 'currency': 'LTC', 
                             'coinbase_account_id': 'A1'}, 
                        headers=AUTH_HEADERS)
                        
    
    async def test_withdraw_payment_method(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.withdraw_payment_method(104.1, 'USD', 'WNNK')
            
        resp = await self.auth_client.withdraw_payment_method(93.5, 'USD', 'WTPA')
        self.check_req(self.mock_post, '{}/withdrawals/payment-method'.format(URL),
                      data={'amount': 93.5, 'currency': 'USD',
                             'payment_method_id': 'WTPA'},
                      headers=AUTH_HEADERS)
        
                        
    async def test_withdrawl_coinbase(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.withdraw_coinbase(1000, 'BTC', '7')
            
        resp =await self.auth_client.withdraw_coinbase(95, 'LTC', 'A1')
        self.check_req(self.mock_post, '{}/withdrawals/coinbase-account'.format(URL),
                      data={'amount': 95, 'currency': 'LTC', 
                             'coinbase_account_id': 'A1'}, 
                      headers=AUTH_HEADERS)
                        
                        
    async def test_withdrawl_crypto(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.withdraw_crypto(83, 'YES', '90125')
            
        resp =await self.auth_client.withdraw_crypto(88, 'VH', 'OU812')
        self.check_req(self.mock_post, '{}/withdrawals/crypto'.format(URL),
                      data={'amount': 88, 'currency': 'VH', 
                             'crypto_address': 'OU812'}, 
                        headers=AUTH_HEADERS)
                        
    
    async def test_stablecoin_conversion(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.stablecoin_conversion('frown', 'smile', 100.1)
            
        resp =await self.auth_client.stablecoin_conversion('USD', 'USDC', 19.72)
        self.check_req(self.mock_post, '{}/conversions'.format(URL),
                       data={'from': 'USD', 'to': 'USDC', 'amount': 19.72}, 
                       headers=AUTH_HEADERS)                       

    
    async def test_fees(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            fees = await self.client.fees()        
        
        fees = await self.auth_client.fees()
        self.check_req(self.mock_get, '{}/fees'.format(URL), headers=AUTH_HEADERS)    


    async def test_create_report(self):
        
        end = datetime.utcnow()
        start = end - timedelta(days=1)
        end = end.isoformat()
        start = start.isoformat()
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.create_report('account', start, end)
            
        # Invalid report type
        with self.assertRaises(ValueError):
            resp = await self.auth_client.create_report('TPS', start, end)
            
        # report_type fills, no product_id
        with self.assertRaises(ValueError):
            resp = await self.auth_client.create_report('fills', start, end)
            
        # report_type accounts, no account_id
        with self.assertRaises(ValueError):
            resp = await self.auth_client.create_report('account', start, end)
            
        # invalid format
        with self.assertRaises(ValueError):
            resp = await self.auth_client.create_report('fills', start, end,
                                                'BTC-USD', report_format='mp3')
                                                
        # report type fills, default format
        resp = await self.auth_client.create_report('fills', start, end, 'BTC_USD')
        self.check_req(self.mock_post, '{}/reports'.format(URL),
                      data={'type': 'fills', 'product_id': 'BTC_USD',
                             'start_date': start, 'end_date': end, 
                             'format': 'pdf'},
                      headers=AUTH_HEADERS)
                       
        # report type account, non-default format, email
        resp = await self.auth_client.create_report('account', start, end, 
                             account_id='R2D2', report_format='csv',
                             email='me@example.com')
        self.check_req(self.mock_post, '{}/reports'.format(URL),
                      data={'type': 'account', 'account_id': 'R2D2',
                             'start_date': start, 'end_date': end,
                             'format': 'csv', 'email': 'me@example.com'},
                      headers=AUTH_HEADERS)
                
            
    async def test_report_status(self):
        
        # Unathorized client
        with self.assertRaises(ValueError):
            resp = await self.client.report_status('mnopuppies')
            
        # No report_id
        with self.assertRaises(TypeError):
            resp = await self.auth_client.report_status()
            
        resp = await self.auth_client.report_status('icmpn')
        self.check_req(self.mock_get, '{}/reports/icmpn'.format(URL), 
                      headers=AUTH_HEADERS)
                       
                       
    async def test_trailing_volume(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.trailing_volume()
            
        resp = await self.auth_client.trailing_volume()
        self.check_req(self.mock_get, 
                      '{}/users/self/trailing-volume'.format(URL),
                      headers=AUTH_HEADERS)
