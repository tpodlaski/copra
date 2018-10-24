#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `copra.rest` module.

Uses http://httpbin.org/ - HTTP Request & Response Service
"""

from dotenv import load_dotenv
load_dotenv()

# KEY = os.getenv('KEY')
# SECRET = os.getenv('SECRET')
# PASSPHRASE = os.getenv('PASSPHRASE')
# TEST_AUTH = True if (KEY and SECRET and PASSPHRASE) else False

# TEST_ACCOUNT = os.getenv('TEST_ACCOUNT')

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
    
    # def test_get_server_time(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             time = await client.get_server_time()
    #             self.assertIsInstance(time, dict)
    #             self.assertIn('iso', time)
    #             self.assertIn('epoch', time)
    #             self.assertIsInstance(time['iso'], str)
    #             self.assertIsInstance(time['epoch'], float)
                
    #     self.loop.run_until_complete(go())
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_products(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         products = await client.get_products()
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products')
            
    #         query = parse_qs(query_str)
    #         self.assertEqual(len(query), 0)
            
    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         headers = mock_get.call_args[1]['headers']
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_order_book(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         with self.assertRaises(TypeError):
    #             ob = await client.get_order_book()
            
    #         with self.assertRaises(ValueError):
    #             ob = await client.get_order_book('BTC-USD', 99)
            
    #         ob = await client.get_order_book('BTC-USD')
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/book')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['level'][0], '1')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         ob = await client.get_order_book('BTC-USD', level=1)
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/book')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['level'][0], '1')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         ob = await client.get_order_book('BTC-USD', level=2)

    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/book')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['level'][0], '2')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         ob = await client.get_order_book('BTC-USD', level=3)
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/book')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['level'][0], '3')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_ticker(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         with self.assertRaises(TypeError):
    #             tick = await client.get_ticker()
            
    #         tick = await client.get_ticker('BTC-USD')
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/ticker')
    #         self.assertEqual(len(query), 0)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_trades(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         with self.assertRaises(TypeError):
    #             trades, before, after = await client.get_trades()
                
    #         with self.assertRaises(ValueError):
    #             trades, before, after = await client.get_trades('BTC-USD', before=1, after=100)
                
    #         trades, before, after = await client.get_trades('BTC-USD')
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/trades')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['limit'][0], '100')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         ret_headers = {'cb-before': '51590012', 'cb-after': '51590010'}

    #         body = [
    #                     {
    #                       'time': '2018-09-27T22:49:16.105Z', 
    #                       'trade_id': 51584925, 
    #                       'price': '6681.01000000', 
    #                       'size': '0.02350019', 
    #                       'side': 'sell'
    #                     }, 
    #                     {
    #                       'time': '2018-09-27T22:49:12.39Z', 
    #                       'trade_id': 51584924, 
    #                       'price': '6681.00000000', 
    #                       'size': '0.01020000', 
    #                       'side': 'buy'
    #                     }
    #               ]
            
    #         mock_get.return_value.__aenter__.return_value.headers = ret_headers
    #         mock_get.return_value.__aenter__.return_value.json.return_value = body
            
    #         trades, before, after = await client.get_trades('BTC-USD', limit=5)
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/trades')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['limit'][0], '5')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         self.assertEqual(trades, body)
    #         self.assertEqual(before, ret_headers['cb-before'])
    #         self.assertEqual(after, ret_headers['cb-after'])
            
    #         prev_trades, prev_before, prev_after = await client.get_trades('BTC-USD', before=before)
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/trades')
    #         self.assertEqual(len(query), 2)
    #         self.assertEqual(query['limit'][0], '100')
    #         self.assertEqual(query['before'][0], before)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         next_trades, next_before, next_after = await client.get_trades('BTC-USD', after=after)
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/trades')
    #         self.assertEqual(len(query), 2)
    #         self.assertEqual(query['limit'][0], '100')
    #         self.assertEqual(query['after'][0], after)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_historic_rates(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         with self.assertRaises(TypeError):
    #             rates = await client.get_historic_rates()
                
    #         with self.assertRaises(ValueError):
    #             rates = await client.get_historic_rates('BTC-USD', granularity=100)
                
    #         rates = await client.get_historic_rates('BTC-USD')
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/candles')
    #         self.assertEqual(len(query), 1)
    #         self.assertEqual(query['granularity'][0], '3600')

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    #         stop = datetime.utcnow()
    #         start = stop - timedelta(days=1)
            
    #         rates = await client.get_historic_rates('BTC-USD', 900, start.isoformat(), stop.isoformat())
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/candles')
    #         self.assertEqual(len(query), 3)
    #         self.assertEqual(query['granularity'][0], '900')
    #         self.assertEqual(query['start'][0], start.isoformat())
    #         self.assertEqual(query['stop'][0], stop.isoformat())
            

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_24hour_stats(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         with self.assertRaises(TypeError):
    #             stats = await client.get_24hour_stats()

    #         stats = await client.get_24hour_stats('BTC-USD')
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/products/BTC-USD/stats')
    #         self.assertEqual(len(query), 0)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
            
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_currencies(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         currencies = await client.get_currencies()
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/currencies')
    #         self.assertEqual(len(query), 0)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)

    # @patch('aiohttp.ClientSession.get')
    # async def test_get_server_time(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         time = await client.get_server_time()
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/time')
    #         self.assertEqual(len(query), 0)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_get_server_time(self, mock_get):
    #     async with Client(self.loop) as client:
            
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
            
    #         time = await client.get_server_time()
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/time')
    #         self.assertEqual(len(query), 0)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT)
    
    # @patch('aiohttp.ClientSession.get')
    # async def test_list_accounts(self, mock_get):
    #     async with Client(self.loop) as client:
    #         with self.assertRaises(ValueError):
    #             accounts = await client.list_accounts()

    #     async with Client(self.loop, auth=True, key=TEST_KEY, secret=TEST_SECRET, 
    #                       passphrase=TEST_PASSPHRASE) as client:
                              
    #         mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
                
    #         accounts = await client.list_accounts()
            
    #         self.assertEqual(len(mock_get.call_args[0]), 1)
    #         self.assertIsInstance(mock_get.call_args[0][0], str)
            
    #         scheme, netloc, path, params, query_str, fragment = urlparse(mock_get.call_args[0][0])
    #         query = parse_qs(query_str)
    #         headers = mock_get.call_args[1]['headers']
            
    #         self.assertEqual('{}://{}'.format(scheme, netloc), URL)
    #         self.assertEqual(path, '/accounts')
    #         self.assertEqual(len(query), 0)

    #         self.assertEqual(len(mock_get.call_args[1]), 1)
    #         self.assertEqual(len(headers), 1)
    #         self.assertEqual(headers['USER-AGENT'], USER_AGENT


    # @unittest.skipUnless(TEST_AUTH, "Authentication credentials not provided.")
    # def test_list_accounts(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             with self.assertRaises(ValueError):
    #                 accounts = await client.list_accounts()
            
    #         async with Client(self.loop, auth=True, key=KEY, secret=SECRET, 
    #                           passphrase=PASSPHRASE) as client:
    #             accounts = await client.list_accounts()
    #             self.assertIsInstance(accounts, list)
    #             self.assertIsInstance(accounts[0], dict)
    #             self.assertIn('id', accounts[0])
    #             self.assertIn('currency', accounts[0])
    #             self.assertIn('balance', accounts[0])
    #             self.assertIn('available', accounts[0])
    #             self.assertIn('hold', accounts[0])
    #             self.assertIn('profile_id', accounts[0])
    
    #     self.loop.run_until_complete(go())
    
    # @unittest.skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    # def test_get_account(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             with self.assertRaises(ValueError):
    #                 acount = await client.get_account(TEST_ACCOUNT)
            
    #         async with Client(self.loop, auth=True, key=KEY, secret=SECRET, 
    #                           passphrase=PASSPHRASE) as client:
    #             account = await client.get_account(TEST_ACCOUNT)
    #             self.assertIsInstance(account, dict)
    #             self.assertIn('id', account)
    #             self.assertIn('currency', account)
    #             self.assertIn('balance', account)
    #             self.assertIn('available', account)
    #             self.assertIn('hold', account)
    #             self.assertIn('profile_id', account)
                
    #     self.loop.run_until_complete(go())
    
    # @unittest.skipUnless(TEST_AUTH and TEST_ACCOUNT, "Auth credentials and test account ID required")
    # def test_get_account_activity(self):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             with self.assertRaises(ValueError):
    #                 activity = await client.get_account_history(TEST_ACCOUNT)
                    
    #         async with Client(self.loop, auth=True, key=KEY, secret=SECRET, 
    #                           passphrase=PASSPHRASE) as client:
    #             results = await client.get_account_history(TEST_ACCOUNT)
    #             self.assertEqual(len(results), 3)
    #             self.assertIsInstance(results[0], list)
    #             self.assertIsInstance(results[0][0], dict)
    #             self.assertIsInstance(results[1], str)
    #             self.assertIsInstance(results[2], str)
                
    #             next_results = await client.get_account_history(TEST_ACCOUNT, after=results[2])
    #             self.assertEqual(len(next_results), 3)
    #             self.assertIsInstance(next_results[0], list)
    #             self.assertIsInstance(next_results[0][0], dict)
    #             self.assertIsInstance(next_results[1], str)
    #             self.assertIsInstance(next_results[2], str)
    #             self.assertLess(next_results[0][0]['id'], results[0][-1]['id'])
                
    #             prev_results = await client.get_account_history(TEST_ACCOUNT, before=next_results[1])
    #             self.assertEqual(prev_results, results)
                
    #             ten_results = await client.get_account_history(TEST_ACCOUNT, limit=10)
    #             self.assertEqual(len(ten_results[0]), 10)
                
    #     self.loop.run_until_complete(go())
    
    #@patch('aiohttp.ClientSession.get')
    # def test_get_holds(self, mock_get):
    #     async def go():
    #         async with Client(self.loop) as client:
    #             with self.assertRaises(ValueError):
    #                 holds, before, after = await client.get_holds('ACCOUNT ID')
                    
    #         holds = [{'key', 'hold place holder'}] 
            
    #         mo = MagicMock()
    #         mo.__aenter__ = MagicMock(return_value = mo)
    #         mo.__aexit__ = MagicMock(return_value = None)
    #         mock_get.return_value = mo
            

    #         async with Client(self.loop, auth=True, key=MOCK_KEY, 
    #                           secret=MOCK_SECRET, 
    #                           passphrase=MOCK_PASSPHRASE) as client:
    #                 holds, before, after = await client.get_holds('ACCOUNT ID')
                    
    #                 print(holds)
        
    #     self.loop.run_until_complete(go())