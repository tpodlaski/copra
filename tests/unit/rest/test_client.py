#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.Client` class.
"""

import asyncio
from datetime import datetime, timedelta
import time

import aiohttp
from asynctest import CoroutineMock, patch, TestCase

from copra.rest import Client, URL, HEADERS
from tests.unit.rest.util import *


TEST_KEY = 'a035b37f42394a6d343231f7f772b99d'
TEST_SECRET = 'aVGe54dHHYUSudB3sJdcQx4BfQ6K5oVdcYv4eRtDN6fBHEQf5Go6BACew4G0iFjfLKJHmWY5ZEwlqxdslop4CC=='
TEST_PASSPHRASE = 'a2f9ee4dx2b'

AUTH_HEADERS = UNAUTH_HEADERS = HEADERS

AUTH_HEADERS.update({
                      'Content-Type': 'Application/JSON',
                      'CB-ACCESS-TIMESTAMP': '*',
                      'CB-ACCESS-SIGN': '*',
                      'CB-ACCESS-KEY': TEST_KEY,
                      'CB-ACCESS-PASSPHRASE': TEST_PASSPHRASE
                    })


class TestRest(TestCase):
    """Tests for copra.rest.Client"""
    
    update_mock_get = update_mock_get
    check_mock_get_args = check_mock_get_args
    check_mock_get_url = check_mock_get_url
    check_mock_get_headers = check_mock_get_headers

    def setUp(self):
        mock_get_patcher = patch('aiohttp.ClientSession.get', new_callable=CoroutineMock)
        self.mock_get = mock_get_patcher.start()
        self.mock_get.side_effect = self.update_mock_get
        self.mock_get.return_value.json = CoroutineMock()
        self.addCleanup(mock_get_patcher.stop)
        
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
                    
        headers = self.auth_client.get_auth_headers('/mypath', 1539968909.917318)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers['Content-Type'], 'Application/JSON')
        self.assertEqual(headers['CB-ACCESS-SIGN'], 'haapGobLuJMel4ku5s7ptzyNkQdYtLPMXgQJq5f1/cg=')
        self.assertEqual(headers['CB-ACCESS-TIMESTAMP'], str(1539968909.917318))
        self.assertEqual(headers['CB-ACCESS-KEY'], TEST_KEY)
        self.assertEqual(headers['CB-ACCESS-PASSPHRASE'], TEST_PASSPHRASE)


    async def test_get(self):
        path = '/mypath'
        query = {'key1': 'item1', 'key2': 'item2'}
        
        #Unauthorized call by unauthorized client
        resp = await self.client.get(path, query)
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, path), query)
        self.check_mock_get_headers(UNAUTH_HEADERS)
        
        #Authorized call by unauthorized client
        with self.assertRaises(ValueError):
            resp = await self.client.get(path, query, auth=True)
            
        #Unauthorized call by authorized client
        resp = await self.auth_client.get(path, query)
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, path), query)
        self.check_mock_get_headers(UNAUTH_HEADERS)
        
        #Authorized call by authorized client
        resp = await self.auth_client.get(path, query, auth=True)
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, path), query)
        self.check_mock_get_headers(AUTH_HEADERS)


    async def test_get_products(self):
        
        products = await self.client.get_products()
            
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products'), {})
        self.check_mock_get_headers(UNAUTH_HEADERS)
            

    async def test_get_order_book(self):            

        with self.assertRaises(TypeError):
            ob = await self.client.get_order_book()
            
        with self.assertRaises(ValueError):
            ob = await self.client.get_order_book('BTC-USD', 99)
            
        #Default level 1
        ob = await self.client.get_order_book('BTC-USD')
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/book'), 
                                {'level': '1'})
        self.check_mock_get_headers(UNAUTH_HEADERS)

        #Level 1
        ob = await self.client.get_order_book('BTC-USD', level=1)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/book'), 
                                {'level': '1'})
        self.check_mock_get_headers(UNAUTH_HEADERS)
            
        #Level 2
        ob = await self.client.get_order_book('BTC-USD', level=2)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/book'), 
                                {'level': '2'})
        self.check_mock_get_headers(UNAUTH_HEADERS)
            
        #Level 3
        ob = await self.client.get_order_book('BTC-USD', level=3)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/book'), 
                                {'level': '3'})
        self.check_mock_get_headers(UNAUTH_HEADERS)

    
    async def test_get_ticker(self):
        
        with self.assertRaises(TypeError):
            tick = await self.client.get_ticker()
            
        tick = await self.client.get_ticker('BTC-USD')
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/ticker'), {})
        self.check_mock_get_headers(UNAUTH_HEADERS)


    async def test_get_trades(self):
        
        with self.assertRaises(TypeError):
            trades, before, after = await self.client.get_trades()
            
        with self.assertRaises(ValueError):
            trades, before, after = await self.client.get_trades('BTC-USD', before=1, after=100)
            
        trades, before, after = await self.client.get_trades('BTC-USD')
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/trades'), 
                                {'limit': '100'})
        self.check_mock_get_headers(UNAUTH_HEADERS)

        ret_headers = {'cb-before': '51590012', 'cb-after': '51590010'}

        body = [
                    {
                      'time': '2018-09-27T22:49:16.105Z', 
                      'trade_id': 51584925, 
                      'price': '6681.01000000', 
                      'size': '0.02350019', 
                      'side': 'sell'
                    }, 
                    {
                      'time': '2018-09-27T22:49:12.39Z', 
                      'trade_id': 51584924, 
                      'price': '6681.00000000', 
                      'size': '0.01020000', 
                      'side': 'buy'
                    }
              ]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
            
        trades, before, after = await self.client.get_trades('BTC-USD', limit=5)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/trades'), 
                                {'limit': '5'})
        self.check_mock_get_headers(UNAUTH_HEADERS)

        self.assertEqual(trades, body)
        self.assertEqual(before, ret_headers['cb-before'])
        self.assertEqual(after, ret_headers['cb-after'])
            
        prev_trades, prev_before, prev_after = await self.client.get_trades('BTC-USD', before=before)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/trades'), 
                                {'limit': '100', 'before': before})
        self.check_mock_get_headers(UNAUTH_HEADERS)
            
        next_trades, next_before, next_after = await self.client.get_trades('BTC-USD', after=after)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/trades'), 
                                {'limit': '100', 'after': after})
        self.check_mock_get_headers(UNAUTH_HEADERS)


    async def test_get_historic_rates(self):
        
        with self.assertRaises(TypeError):
            rates = await self.client.get_historic_rates()
            
        with self.assertRaises(ValueError):
            rates = await self.client.get_historic_rates('BTC-USD', granularity=100)
            
        rates = await self.client.get_historic_rates('BTC-USD')
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/candles'), 
                                {'granularity': '3600'})
        self.check_mock_get_headers(UNAUTH_HEADERS)
            
        stop = datetime.utcnow()
        start = stop - timedelta(days=1)
            
        rates = await self.client.get_historic_rates('BTC-USD', 900, 
                                                     start.isoformat(), 
                                                     stop.isoformat())
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/candles'), 
                                {'granularity': '900', 
                                 'start': start.isoformat(), 
                                 'stop': stop.isoformat()
                                })
        self.check_mock_get_headers(UNAUTH_HEADERS)
            
            
    async def test_get_24hour_stats(self):

        with self.assertRaises(TypeError):
            stats = await self.client.get_24hour_stats()

        stats = await self.client.get_24hour_stats('BTC-USD')
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/products/BTC-USD/stats'), {})
        self.check_mock_get_headers(UNAUTH_HEADERS)


    async def test_get_currencies(self):

        currencies = await self.client.get_currencies()
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/currencies'), {})
        self.check_mock_get_headers(UNAUTH_HEADERS)
        
    async def test_get_server_time(self):
        
        time = await self.client.get_server_time()
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/time'), {})
        self.check_mock_get_headers(UNAUTH_HEADERS)
         

    async def test_list_accounts(self):
        
        with self.assertRaises(ValueError):
            accounts = await self.client.list_accounts()        
        
        accounts = await self.auth_client.list_accounts()
                
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts'), {})
        self.check_mock_get_headers(AUTH_HEADERS)

    
    async def test_get_account(self):

        with self.assertRaises(TypeError):
            trades, before, after = await self.auth_client.get_account()        

        with self.assertRaises(ValueError):
            acount = await self.client.get_account(42)
            
        account = await self.auth_client.get_account(42)    

        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42'), {})
        self.check_mock_get_headers(AUTH_HEADERS)

    
    async def test_get_account_history(self):

        with self.assertRaises(TypeError):
            trades, before, after = await self.auth_client.get_account_history()
            
        with self.assertRaises(ValueError):
            trades, before, after = await self.client.get_account_history(42)
            
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}

        body = [
                 {
                  'created_at': '2018-09-28T19:31:21.211159Z', 
                  'id': 10712040275, 
                  'amount': '-600.9103845810000000', 
                  'balance': '0.0000005931528000', 'type': 
                  'match', 
                  'details': {
                                'order_id': 'd2fadbb5-8769-4b80-91da-be3d9c6bd38d', 
                                'trade_id': '34209042', 
                                'product_id': 'BTC-USD'
                              }
                 }, 
                 {
                  'created_at': '2018-09-23T23:13:45.771507Z', 
                  'id': 1065316993, 
                  'amount': '-170.0000000000000000', 
                  'balance': '6.7138918107528000', 
                  'type': 'transfer', 
                  'details': {
                                'transfer_id': 'd00841ff-c572-4726-b9bf-17e783159256', 
                                'transfer_type': 'withdraw'
                              }
                 }
              ]
        
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body

        trades, before, after = await self.auth_client.get_account_history(42, limit=5)
        
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(trades, body)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42/ledger'), 
                              {'limit': '5'})
        self.check_mock_get_headers(AUTH_HEADERS)
        
        trades, before, after = await self.auth_client.get_account_history(42, before=before)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42/ledger'), 
                              {'limit': '100', 'before': before})
        self.check_mock_get_headers(AUTH_HEADERS)       

        trades, before, after = await self.auth_client.get_account_history(42, after=after)
        
         
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42/ledger'), 
                              {'limit': '100', 'after': after})
        self.check_mock_get_headers(AUTH_HEADERS)  


    async def test_get_holds(self):
        
        with self.assertRaises(TypeError):
            holds, before, after = await self.auth_client.get_holds()
            
        with self.assertRaises(ValueError):
            holds, before, after = await self.client.get_holds(42)
            
        ret_headers = {'cb-before': '1071064024', 'cb-after': '1008063508'}
        
        body = [
                 {
                  "id": "82dcd140-c3c7-4507-8de4-2c529cd1a28f",
                  "account_id": "e0b3f39a-183d-453e-b754-0c13e5bab0b3",
                  "created_at": "2014-11-06T10:34:47.123456Z",
                  "updated_at": "2014-11-06T10:40:47.123456Z",
                  "amount": "4.23",
                  "type": "order",
                  "ref": "0a205de4-dd35-4370-a285-fe8fc375a273",
                  }
                ]
                
        self.mock_get.return_value.headers = ret_headers
        self.mock_get.return_value.json.return_value = body
                
        holds, before, after = await self.auth_client.get_holds(42, limit=5)
        
        self.assertEqual(before, '1071064024')
        self.assertEqual(after, '1008063508')
        self.assertEqual(holds, body)
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42/holds'), 
                              {'limit': '5'})
        self.check_mock_get_headers(AUTH_HEADERS)
        
        holds, before, after = await self.auth_client.get_holds(42, before=before)
                                                              
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42/holds'), 
                              {'limit': '100', 'before': before})
        self.check_mock_get_headers(AUTH_HEADERS)
        
        holds, before, after = await self.auth_client.get_holds(42, after=after)
                                                              
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/accounts/42/holds'), 
                              {'limit': '100', 'after': after})
        self.check_mock_get_headers(AUTH_HEADERS)

      
    async def test_place_order(self):
        
        with self.assertRaises(ValueError):
            resp = await self.client.place_order('sell', 'BTC-USD')
        
        with self.assertRaises(ValueError):
            resp = await self.client.place_order("give away", 'BTC-USD')
            
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
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/orders'), 
                              {'side': 'buy', 
                                'product_id': 'BTC-USD',
                                'order_type': 'limit',
                                'price': '100.1',
                                'size': '5',
                                'time_in_force': 'GTC',
                                'post_only': 'True',
                                'stp': 'dc'
                              })
        self.check_mock_get_headers(AUTH_HEADERS)
                              
        # GTT order with cancel_after
        resp = await self.auth_client.place_order('buy', 'BTC-USD',
                            price=300, size=88, order_type='limit',
                            time_in_force='GTT', cancel_after='hour')
                            
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/orders'), 
                              {'side': 'buy', 
                                'product_id': 'BTC-USD',
                                'order_type': 'limit',
                                'price': '300',
                                'size': '88',
                                'time_in_force': 'GTT',
                                'cancel_after': 'hour',
                                'post_only': 'True',
                                'stp': 'dc'
                              })
        self.check_mock_get_headers(AUTH_HEADERS)                               
        
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
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/orders'), 
                              {'side': 'buy', 
                                'product_id': 'BTC-USD',
                                'order_type': 'market',
                                'size': '5',
                                'stp': 'dc'
                              })
        self.check_mock_get_headers(AUTH_HEADERS) 
        
        # Funds
        resp = await self.auth_client.place_order('buy', 'BTC-USD', funds=1000, 
                                                  order_type='market')
        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/orders'), 
                              {'side': 'buy', 
                                'product_id': 'BTC-USD',
                                'order_type': 'market',
                                'funds': '1000',
                                'stp': 'dc'
                              })
        self.check_mock_get_headers(AUTH_HEADERS)
        
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
                        
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/orders'), 
                              {'side': 'buy', 
                              'product_id': 'BTC-USD',
                              'order_type': 'limit',
                              'price': '100.1',
                              'size': '5',
                              'time_in_force': 'GTC',
                              'post_only': 'True',
                              'stop': 'loss',
                              'stop_price': '105',
                              'stp': 'dc'
                              })
        self.check_mock_get_headers(AUTH_HEADERS)
        
        # Valid order with client_oid and stp set
        resp = await self.auth_client.place_order('buy', 'BTC-USD', price=100.1, 
            size=5, client_oid=42, stp='co')
         
        self.check_mock_get_args([str], {'headers': dict})
        self.check_mock_get_url('{}{}'.format(URL, '/orders'), 
                              {'side': 'buy', 
                                'product_id': 'BTC-USD',
                                'order_type': 'limit',
                                'price': '100.1',
                                'size': '5',
                                'time_in_force': 'GTC',
                                'post_only': 'True',
                                'client_oid': '42',
                                'stp': 'co'
                              })
        self.check_mock_get_headers(AUTH_HEADERS)
        