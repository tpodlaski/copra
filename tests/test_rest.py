#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `copra.rest` module.

Uses http://httpbin.org/ - HTTP Request & Response Service
"""

import asyncio
from datetime import datetime, timedelta
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
    
    # def test__init__(self):
    #     async def go():
    #         client = Client(self.loop)
    #         self.assertEqual(client.url, 'https://api.pro.coinbase.com')
    #         await client.close()
            
    #         client = Client(self.loop, 'http://httpbin.org/')
    #         self.assertEqual(client.url, 'http://httpbin.org/')
    #         await client.close()
        
    #     self.loop.run_until_complete(go())
        
    # def test_close(self):
    #     async def go():
    #         client = Client(self.loop)
    #         self.assertFalse(client.session.closed)
            
    #         await client.close()
    #         self.assertTrue(client.session.closed)
            
    #     self.loop.run_until_complete(go())
        
    # def test_context_manager(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             self.assertFalse(client.session.closed)
    #         self.assertTrue(client.session.closed)
            
    #         try:
    #             async with Client(self.loop) as client:
    #                 self.assertFalse(client.session.closed)
    #                 #Throws ValueError
    #                 ob = await client.get_order_book('BTC-USD', level=99)
    #         except ValueError as e:
    #             pass
    #         self.assertTrue(client.session.closed)
            
    #     self.loop.run_until_complete(go())
        
    # def test_get(self):
    #     async def go():
    #         async with Client(self.loop, 'http://httpbin.org/') as client:
    #             params = {'key1': 'item1', 'key2': 'item2'}
    #             fullresp = await client.get('/get', params)
    #             self.assertEqual(len(fullresp), 2)
    #             headers, body = fullresp[:]
    #             self.assertIsInstance(headers, dict)
    #             self.assertIn('Content-Length', headers)
    #             self.assertIsInstance(body, dict)
    #             self.assertEqual(len(body['args']), 2)
    #             self.assertEqual(body['args']['key1'], 'item1')
    #             self.assertEqual(body['args']['key2'], 'item2')
    #             self.assertEqual(body['url'], 'http://httpbin.org/get?key1=item1&key2=item2')

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
            
    # def test_get_order_book(self):
    #     async def go():
    #         async with Client(self.loop) as client:
            
    #             with self.assertRaises(ValueError):
    #                 ob = await client.get_order_book('BTC-USD', 99)
                
    #             ob1 = await client.get_order_book('BTC-USD')
    #             self.assertIsInstance(ob1, dict)
    #             self.assertEqual(len(ob1), 3)
    #             self.assertIn('sequence', ob1)
    #             self.assertIn('bids', ob1)
    #             self.assertIn('asks', ob1)
    #             self.assertEqual(len(ob1['bids']), 1)
    #             self.assertEqual(len(ob1['asks']), 1)
            
    #             ob1 = await client.get_order_book('BTC-USD', level=1)
    #             self.assertIsInstance(ob1, dict)
    #             self.assertEqual(len(ob1), 3)
    #             self.assertIn('sequence', ob1)
    #             self.assertIn('bids', ob1)
    #             self.assertIn('asks', ob1)
    #             self.assertEqual(len(ob1['bids']), 1)
    #             self.assertEqual(len(ob1['asks']), 1)
            
    #             ob2 = await client.get_order_book('BTC-USD', level=2)
    #             self.assertIsInstance(ob2, dict)
    #             self.assertEqual(len(ob2), 3)
    #             self.assertIn('sequence', ob2)
    #             self.assertIn('bids', ob2)
    #             self.assertIn('asks', ob2)
    #             self.assertEqual(len(ob2['bids']), 50)
    #             self.assertEqual(len(ob2['asks']), 50)
            
    #             ob3 = await client.get_order_book('BTC-USD', level=3)
    #             self.assertIsInstance(ob3, dict)
    #             self.assertEqual(len(ob3), 3)
    #             self.assertIn('sequence', ob3)
    #             self.assertIn('bids', ob3)
    #             self.assertIn('asks', ob3)
    #             self.assertGreater(len(ob3['bids']), 50)
    #             self.assertGreater(len(ob3['asks']), 50)
            
    #     self.loop.run_until_complete(go())
        
    # def test_get_ticker(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             tick = await client.get_ticker('BTC-USD')
    #             self.assertIsInstance(tick, dict)
    #             self.assertIn('trade_id', tick)
    #             self.assertIn('price', tick)
    #             self.assertIn('size', tick)
    #             self.assertIn('bid', tick)
    #             self.assertIn('ask', tick)
    #             self.assertIn('volume', tick)
    #             self.assertIn('time', tick)
                
    #     self.loop.run_until_complete(go())
    
    # def test_get_trades(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             trades, before, after = await client.get_trades('BTC-USD')
    #             self.assertIsInstance(trades, list)
    #             self.assertIsInstance(before, str)
    #             self.assertIsInstance(after, str)
    #             self.assertEqual(len(trades), 100)
    #             self.assertIn('time', trades[0])
    #             self.assertIn('trade_id', trades[0])
    #             self.assertIn('price', trades[0])
    #             self.assertIn('size', trades[0])
    #             self.assertIn('side', trades[0])
                
    #             trades, before, after = await client.get_trades('BTC-USD', 5)
    #             self.assertIsInstance(trades, list)
    #             self.assertEqual(len(trades), 5)
                
    #             trades_after, after_after, before_after = await client.get_trades('BTC-USD', 5, after=after)
    #             self.assertIsInstance(trades_after, list)
    #             self.assertEqual(len(trades_after), 5)
    #             self.assertLess(trades_after[0]['trade_id'], trades[-1]['trade_id'])
                
    #             trades_before, after_before, before_before = await client.get_trades('BTC-USD', 5, before=before)
    #             if (trades_before):
    #                 self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
    #             else:
    #                 self.assertIsNone(after_before)
    #                 self.assertIsInstance(after_after, str)
                    
    #             await asyncio.sleep(20)
                
    #             trades_before, after_before, before_before = await client.get_trades('BTC-USD', 5, before=before)
    #             if (trades_before):
    #                 self.assertGreater(trades_before[-1]['trade_id'], trades[0]['trade_id'])
    #             else:
    #                 self.assertIsNone(after_before)
    #                 self.assertIsInstance(after_after, str)

    #     self.loop.run_until_complete(go())
    
    # def test_get_historic_rates(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             with self.assertRaises(ValueError):
    #                 rates = await client.get_historic_rates('BTC-USD', granularity=100)
                    
    #             rates = await client.get_historic_rates('BTC-USD', 900)
    #             self.assertIsInstance(rates, list)
    #             self.assertGreaterEqual(len(rates), 300)
    #             self.assertEqual(len(rates[0]), 6)
    #             self.assertEqual(rates[0][0] - rates[1][0], 900)
                
    #             stop = datetime.utcnow()
    #             start = stop - timedelta(days=1)
    #             rates = await client.get_historic_rates('LTC-USD', 3600, start.isoformat(), stop.isoformat())
    #             self.assertIsInstance(rates, list)
    #             self.assertEqual(len(rates), 24)
    #             self.assertEqual(len(rates[0]), 6)
    #             self.assertEqual(rates[0][0] - rates[1][0], 3600)
                
        
    #     self.loop.run_until_complete(go())
    
    # def test_get_24hour_stats(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             stats = await client.get_24hour_stats('BTC-USD')
    #             self.assertIsInstance(stats, dict)
    #             self.assertEqual(len(stats), 6)
    #             self.assertIn('open', stats)
    #             self.assertIn('high', stats)
    #             self.assertIn('low', stats)
    #             self.assertIn('volume', stats)
    #             self.assertIn('last', stats)
    #             self.assertIn('volume_30day', stats)
            
    #     self.loop.run_until_complete(go())
    
    # def test_get_currencies(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             currencies = await client.get_currencies()
    #             self.assertIsInstance(currencies, list)
    #             self.assertGreater(len(currencies), 1)
    #             self.assertIsInstance(currencies[0], dict)
    #             self.assertIn('id', currencies[0])
    #             self.assertIn('name', currencies[0])
    #             self.assertIn('min_size', currencies[0])
    #             self.assertIn('status', currencies[0])
    #             self.assertIn('message', currencies[0])
            
    #     self.loop.run_until_complete(go())
    
    def test_get_server_time(self):
        async def go():
            async with Client(self.loop) as client:
                time = await client.get_server_time()
                self.assertIsInstance(time, dict)
                self.assertIn('iso', time)
                self.assertIn('epoch', time)
                self.assertIsInstance(time['iso'], str)
                self.assertIsInstance(time['epoch'], float)
                
        self.loop.run_until_complete(go())
            
            