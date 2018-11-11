#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.Client` class.
"""

import asyncio
from datetime import datetime, timedelta
import time

import aiohttp
from asynctest import CoroutineMock
from multidict import MultiDict

from copra.rest import Client, URL, HEADERS
from tests.unit.rest.util import MockTestCase


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
        self.assertEqual(self.client.url, URL)
        self. assertFalse(self.client.auth)

        async with Client(self.loop, 'http://www.test.server') as client:
            self.assertEqual(client.url,'http://www.test.server')
            
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


    async def test_get_auth_headers(self):
        
        async with Client(self.loop) as client:
            with self.assertRaises(ValueError):
                client.get_auth_headers('/mypath')
                    
        path = '/mypath'
        timestamp = 1539968909.917318
        
        # Default GET
        headers = self.auth_client.get_auth_headers(path, timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'haapGobLuJMel4ku5s7ptzyNkQdYtLPMXgQJq5f1/cg=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)
        
        # Explicit GET
        headers = self.auth_client.get_auth_headers(path, method='GET', timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'haapGobLuJMel4ku5s7ptzyNkQdYtLPMXgQJq5f1/cg=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)
        
        # POST
        headers = self.auth_client.get_auth_headers(path, method='POST', timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'Geo8uJefQp5CG42SYsmKW1lvR7t+28ujcgt3yRM1mpA=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)

        # DELETE
        headers = self.auth_client.get_auth_headers(path, method='DELETE', timestamp=timestamp)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'NRdGfZaOAkFK2ENVDJQ43Rg+fLm+6vg4PML/yzmtuiY=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(timestamp))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)
        
        
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
        
        expected_headers = self.auth_client.get_auth_headers(path, 'DELETE', timestamp=self.mock_del.headers['CB-ACCESS-TIMESTAMP'])
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
        
        expected_headers = self.auth_client.get_auth_headers(path, 'GET', timestamp=self.mock_get.headers['CB-ACCESS-TIMESTAMP'])
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
        
        expected_headers = self.auth_client.get_auth_headers(path, 'POST', body=data, timestamp=self.mock_post.headers['CB-ACCESS-TIMESTAMP'])
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
        
        with self.assertRaises(TypeError):
            tick = await self.client.ticker()
            
        tick = await self.client.ticker('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/ticker'.format(URL), 
                       headers=UNAUTH_HEADERS)


    async def test_trades(self):
        
        with self.assertRaises(TypeError):
            trades, before, after = await self.client.trades()
            
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
            
        # Default granularity
        rates = await self.client.historic_rates('BTC-USD')
        self.check_req(self.mock_get, '{}/products/BTC-USD/candles'.format(URL),
                       query={'granularity': '3600'}, headers=UNAUTH_HEADERS)

        stop = datetime.utcnow()
        start = stop - timedelta(days=1)
            
        # Custom granularity, start, stop
        rates = await self.client.historic_rates('BTC-USD', 900, 
                                                 start.isoformat(), 
                                                 stop.isoformat())
        self.check_req(self.mock_get, '{}/products/BTC-USD/candles'.format(URL),
                       query={'granularity': '900', 'start': start.isoformat(),
                              'stop': stop.isoformat()},
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


    async def test_get_account_history(self):

        # No account_id
        with self.assertRaises(TypeError):
            trades, before, after = await self.auth_client.get_account_history()
        
        # Unauthorized client        
        with self.assertRaises(ValueError):
            trades, before, after = await self.client.get_account_history(42)
            
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}
        body = [{'id': '1'}, {'id': '2'}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body

        trades, before, after = await self.auth_client.get_account_history(42, limit=5)
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(trades, body)
        self.check_req(self.mock_get, '{}/accounts/42/ledger'.format(URL), 
                       query={'limit': '5'}, headers=AUTH_HEADERS)
        
        
        trades, before, after = await self.auth_client.get_account_history(42, before=before)
        self.check_req(self.mock_get, '{}/accounts/42/ledger'.format(URL), 
                       query={'limit': '100', 'before': before}, headers=AUTH_HEADERS)
        
        trades, before, after = await self.auth_client.get_account_history(42, after=after)
        self.check_req(self.mock_get, '{}/accounts/42/ledger'.format(URL), 
                       query={'limit': '100', 'after': after}, headers=AUTH_HEADERS)
 

    async def test_get_holds(self):
        
        # No account_id
        with self.assertRaises(TypeError):
            holds, before, after = await self.auth_client.get_holds()
            
        # Unauthorized client
        with self.assertRaises(ValueError):
            holds, before, after = await self.client.get_holds(42)
            
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}
        body = [{'id': '1'}, {'id': '2'}]

        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
                
        holds, before, after = await self.auth_client.get_holds(42, limit=5)
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(holds, body)
        self.check_req(self.mock_get, '{}/accounts/42/holds'.format(URL), 
                       query={'limit': '5'}, headers=AUTH_HEADERS)
        
        holds, before, after = await self.auth_client.get_holds(42, before=before)
        self.check_req(self.mock_get, '{}/accounts/42/holds'.format(URL), 
                       query={'limit': '100', 'before': before}, headers=AUTH_HEADERS)                                                    
        
        holds, before, after = await self.auth_client.get_holds(42, after=after)
        self.check_req(self.mock_get, '{}/accounts/42/holds'.format(URL), 
                       query={'limit': '100', 'after': after}, headers=AUTH_HEADERS)


    async def test_place_order(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.place_order('sell', 'BTC-USD')
        
        # Invalid side
        with self.assertRaises(ValueError):
            resp = await self.client.place_order("give away", 'BTC-USD')
            
        # Invalid price
        with self.assertRaises(ValueError):
            resp = await self.client.place_order('sell', 'BTC-USD', 'free' )
            
        # Invalid stp
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD',
                                            price=100.1, size=5, stp='Plush')
            
        # Limit orders #############################################
        
        # No price or size
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 'limit')
            
        # Price no size
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 'limit',
                                                      price=500)
                                                      
        # Size no price
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 'limit',
                                                      size=5)
                                                      
        # Invalid time_in_force
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 'limit',
                                                      price=100, size=5,
                                                      time_in_force='OPP')
                                                      
        # cancel_after wrong time_in_force
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 'limit',
                                                      price=100, size=5,
                                                      time_in_force='FOK',
                                                      cancel_after='hour')
                                                      
        # invalid cancel_after
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 'limit',
                                                      price=100, size=5,
                                                      time_in_force='GTT',
                                                      cancel_after='lifetime')
        
        # Default order_type, time_in_force
        resp = await self.auth_client.place_order('buy', 'BTC-USD',
                                                  price=100.1, size=5)
        
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                       data={'side': 'buy', 'product_id': 'BTC-USD',
                             'order_type': 'limit', 'price': 100.1,
                             'size': 5, 'time_in_force': 'GTC', 
                             'post_only': True, 'stp': 'dc'},
                       headers=AUTH_HEADERS)

        # GTT order with cancel_after
        resp = await self.auth_client.place_order('buy', 'BTC-USD',
                            price=300, size=88, order_type='limit',
                            time_in_force='GTT', cancel_after='hour')
                            
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                       data={'side': 'buy', 'product_id': 'BTC-USD',
                             'order_type': 'limit', 'price': 300, 'size': 88, 
                             'time_in_force': 'GTT', 'cancel_after': 'hour',
                             'post_only': True, 'stp': 'dc'},
                        headers=AUTH_HEADERS)
        
        # Market orders #############################################
        
        # No funds or size
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD',
                                                      order_type='market')
                                                      
        # Both funds and size
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD',
                                     size=5, funds=100, order_type='market')        
        
        # Size
        resp = await self.auth_client.place_order('buy', 'BTC-USD', size=5, 
                                                  order_type='market')
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                       data={'side': 'buy', 'product_id': 'BTC-USD',
                             'order_type': 'market', 'size': 5, 'stp': 'dc'},
                       headers=AUTH_HEADERS)
        
        # Funds
        resp = await self.auth_client.place_order('buy', 'BTC-USD', funds=100, 
                                                  order_type='market')
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                       data={'side': 'buy', 'product_id': 'BTC-USD',
                             'order_type': 'market', 'funds': 100, 'stp': 'dc'},
                       headers=AUTH_HEADERS)

        # Stop orders #############################################
        
        # Invalid stop
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 
                        price=100.1, size=5, stop='in the name of love',
                        stop_price=500)
                        
        # stop but no stop_price
        with self.assertRaises(ValueError):
            resp = await self.auth_client.place_order('buy', 'BTC-USD', 
                        price=100.1, size=5, stop='loss')
                        
        # Valid stop order
        resp = await self.auth_client.place_order('buy', 'BTC-USD', price=100.1, 
                        size=5, stop='loss', stop_price=105)
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                       data={'side': 'buy', 'product_id': 'BTC-USD',
                             'order_type': 'limit', 'price': 100.1, 'size': 5,
                             'time_in_force': 'GTC', 'post_only': True,
                             'stop': 'loss', 'stop_price': 105, 'stp': 'dc'},
                        headers=AUTH_HEADERS)
                        
        # Valid order with client_oid and stp set
        resp = await self.auth_client.place_order('buy', 'BTC-USD', price=100.1, 
                                                size=5, client_oid=42, stp='co')
        self.check_req(self.mock_post, '{}/orders'.format(URL),
                       data={'side': 'buy', 'product_id': 'BTC-USD',
                             'order_type': 'limit', 'price': 100.1, 'size': 5,
                             'time_in_force': 'GTC', 'post_only': True,
                             'client_oid': 42, 'stp': 'co'},
                        headers=AUTH_HEADERS)


    async def test_cancel_order(self):
        
        with self.assertRaises(TypeError):
            resp = await self.auth_client.cancel_order()
            
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.cancel_order(42)
            
        resp = await self.auth_client.cancel_order(42)
        self.check_req(self.mock_del, '{}/orders/42'.format(URL), headers=AUTH_HEADERS)

        
    async def test_cancel_all(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.cancel_all()
            
        # No product_id
        resp = await self.auth_client.cancel_all()
        self.check_req(self.mock_del, '{}/orders'.format(URL), headers=AUTH_HEADERS)
        
        # product_id
        resp = await self.auth_client.cancel_all('BTC-USD')
        self.check_req(self.mock_del, '{}/orders'.format(URL), 
                       query={'product_id': 'BTC-USD'}, headers=AUTH_HEADERS)


    async def test_list_orders(self):
        
        # Unauthorizerd client
        with self.assertRaises(ValueError):
            orders, before, after = await self.client.list_orders()
        
        # Invalid status string
        with self.assertRaises(ValueError):
            orders, before, after = await self.auth_client.list_orders('fresh')
            
        # Invalid status string in list
        with self.assertRaises(ValueError):
            orders, before, after = await self.auth_client.list_orders(['open', 'stale', 'pending'])
            
        # Default status, default product_id, default limit
        orders, before, after = await self.auth_client.list_orders()
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                       query={'limit': '100'}, headers=AUTH_HEADERS)
        
        # String status, default product_id, default limit
        orders, before, after = await self.auth_client.list_orders('open')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                       query={'limit': '100', 'status': 'open'}, headers=AUTH_HEADERS)
        
        # List status, default product_id, default limit
        orders, before, after = await self.auth_client.list_orders(['pending', 'open'])
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query=MultiDict([('limit', '100'), ('status', 'pending'), ('status', 'open')]),
                      headers=AUTH_HEADERS)        
        
        # product_id, default status, default limit
        orders, before, after = await self.auth_client.list_orders(product_id='BTC-USD')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query={'product_id': 'BTC-USD', 'limit': '100'},
                      headers=AUTH_HEADERS)
                       
        # product_id, string status, default limit
        orders, before, after = await self.auth_client.list_orders('open', 'BTC-USD')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                       query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '100'},
                       headers=AUTH_HEADERS)
                       
        # product_id, list status, default limit
        orders, before, after = await self.auth_client.list_orders(['pending', 'active'], 'BTC-USD')
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                      query=MultiDict([('status', 'pending'), ('status', 'active'), ('product_id','BTC-USD'), ('limit', '100')]),
                      headers=AUTH_HEADERS)
                      
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}

        body = [{'order_id': '1'}, {'order_id': '2'}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
        
        # product_id, list_status, custom limit
        orders, before, after = await self.auth_client.list_orders('open', 'BTC-USD', limit=5)
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(orders, body)
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                       query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '5'},
                       headers=AUTH_HEADERS)
                       
        orders, before, after = await self.auth_client.list_orders('open', 'BTC-USD', before=before)
        self.check_req(self.mock_get, '{}/orders'.format(URL), 
                       query={'status': 'open', 'product_id': 'BTC-USD', 'limit': '100', 'before': before},
                       headers=AUTH_HEADERS)
                       
        orders, before, after = await self.auth_client.list_orders('open', 'BTC-USD', after=after)
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
        
        
    async def test_get_fills(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            fills, before, after = await self.client.list_fills()
            
        # order_id and product_id not defined
        with self.assertRaises(ValueError):
            fills, before, after = await self.auth_client.list_fills()
            
        # order_id and product_id both defined
        with self.assertRaises(ValueError):
            fills, before, after = await self.auth_client.list_fills('42', 'BTC-USD')
        
        # order_id
        fills, before, after = await self.auth_client.list_fills('42')
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                       query={'order_id': '42', 'limit': '100'}, headers=AUTH_HEADERS)
                       
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}

        body = [{'trade_id': '1'}, {'trade_id': '2'}]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
        
        # product_id
        fills, before, after = await self.auth_client.list_fills(product_id='BTC-USD')
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                       query={'product_id': 'BTC-USD', 'limit': '100'}, headers=AUTH_HEADERS)  
        
        # limit, before cursor
        fills, before, after = await self.auth_client.list_fills('42', limit=5, before=before)
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                       query={'order_id': '42', 'limit': '5', 'before': before}, 
                       headers=AUTH_HEADERS)
                       
        # after cursor
        fills, before, after = await self.auth_client.list_fills('42', after=after)
        self.check_req(self.mock_get, '{}/fills'.format(URL),
                       query={'order_id': '42', 'limit': '100', 'after': after}, 
                       headers=AUTH_HEADERS)
                       

    async def test_list_payment_methods(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            methods = await self.client.list_payment_methods()
            
        methods = await self.auth_client.list_payment_methods()
        self.check_req(self.mock_get, '{}/payment-methods'.format(URL), headers=AUTH_HEADERS)
        
        
    async def test_list_coinbase_accounts(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            accounts = await self.client.list_coinbase_accounts()
            
        accounts = await self.auth_client.list_coinbase_accounts()
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
                       data={'from_currency_id': 'USD', 
                             'to_currency_id': 'USDC', 
                             'amount': 19.72}, 
                        headers=AUTH_HEADERS)                       
    

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
                       data={'report_type': 'fills', 'product_id': 'BTC_USD',
                             'start_date': start, 'end_date': end, 
                             'report_format': 'pdf'},
                       headers=AUTH_HEADERS)
                       
        # report type account, non-default format, email
        resp = await self.auth_client.create_report('account', start, end, 
                             account_id='R2D2', report_format='csv',
                             email='me@example.com')
        self.check_req(self.mock_post, '{}/reports'.format(URL),
                       data={'report_type': 'account', 'account_id': 'R2D2',
                             'start_date': start, 'end_date': end,
                             'report_format': 'csv', 'email': 'me@example.com'},
                       headers=AUTH_HEADERS)
                
            
    async def test_get_report_status(self):
        
        # Unathorized client
        with self.assertRaises(ValueError):
            resp = await self.client.get_report_status('mnopuppies')
            
        # No report_id
        with self.assertRaises(TypeError):
            resp = await self.auth_client.get_report_status()
            
        resp = await self.auth_client.get_report_status('icmpn')
        self.check_req(self.mock_get, '{}/reports/icmpn'.format(URL), 
                       headers=AUTH_HEADERS)
                       
                       
    async def test_get_trailing_volume(self):
        
        # Unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.get_trailing_volume()
            
        resp = await self.auth_client.get_trailing_volume()
        self.check_req(self.mock_get, 
                       '{}/users/self/trailing-volume'.format(URL),
                       headers=AUTH_HEADERS)
        
            
        
        
            
    