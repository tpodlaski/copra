#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cbprotk.websocket` module."""

import asyncio
import json
import unittest

from copra.websocket import Channel, ClientProtocol, Client
from copra.websocket import SANDBOX_FEED_URL

class TestChannel(unittest.TestCase):
    """Tests for cbprotk.websocket.Channel"""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test__init__(self):
        #no channel name, no product_ids
        with self.assertRaises(TypeError):
            channel = Channel()
            
        #channel name, no product_ids:
        with self.assertRaises(TypeError):
            channel = Channel('heartbeat')        
            
        #valid name
        channel = Channel('heartbeat', 'BTC-USD')
        self.assertEqual(channel.name, 'heartbeat')

        #invalid name
        with self.assertRaises(ValueError):
            channel = Channel('pulse', 'BTC-USD')
            
        #lower case
        channel = Channel('TiCKeR', 'BTC-USD')
        self.assertEqual(channel.name, 'ticker')
        
        #product_ids as str
        channel = Channel('heartbeat', 'BTC-USD')
        self.assertIsInstance(channel.product_ids, set)
        self.assertEqual(channel.product_ids, set(['BTC-USD']))
        
        #product_ids as list length 1
        channel = Channel('heartbeat', ['BTC-USD'])
        self.assertIsInstance(channel.product_ids, set)
        self.assertEqual(channel.product_ids, set(['BTC-USD']))
        
        #product_ids as list length 2
        channel = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        self.assertIsInstance(channel.product_ids, set)
        self.assertEqual(channel.product_ids, set(['BTC-USD', 'LTC-USD']))
        
        #empty product_ids string
        with self.assertRaises(ValueError):
            channel = Channel('heartbeat', '')
            
        #empty product_ids list
        with self.assertRaises(ValueError):
            channel = Channel('heartbeat', [])
            
    def test_as_dict(self):
        channel = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        d = channel.as_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['name'], 'heartbeat')
        self.assertEqual(len(d['product_ids']), 2)
        self.assertIn('BTC-USD', d['product_ids'])
        self.assertIn('LTC-USD', d['product_ids'])
        
    def test___eq__(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel3 = Channel('heartbeat', 'BTC-USD')
        channel4 = Channel('heartbeat', ['BTC-USD'])
        channel5 = Channel('ticker', ['BTC-USD'])
        
        self.assertEqual(channel1, channel2)
        self.assertEqual(channel3, channel4)
        self.assertNotEqual(channel1, channel3)
        with self.assertRaises(TypeError):
            comp = (channel4 == channel5)
        
    def test___add__(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('heartbeat', ['BTC-EUR', 'LTC-EUR'])
        channel3 = Channel('heartbeat', 'BTC-USD')
        channel4 = Channel('ticker', ['BTC-EUR', 'LTC-EUR'])
        
        channel = channel1 + channel2
        self.assertEqual(channel.name, 'heartbeat')
        self.assertEqual(channel.product_ids, {'BTC-USD', 'LTC-USD', 'BTC-EUR', 'LTC-EUR'})
        
        channel = channel1 + channel3
        self.assertEqual(channel.name, "heartbeat")
        self.assertEqual(channel.product_ids, {'BTC-USD', 'LTC-USD'})
        
        channel1 += channel2
        self.assertEqual(channel1.name, 'heartbeat')
        self.assertEqual(channel1.product_ids, {'BTC-USD', 'LTC-USD', 'BTC-EUR', 'LTC-EUR'})
        
        with self.assertRaises(TypeError):
            channel = channel1 + channel4
            
    def test___sub__(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel3 = Channel('heartbeat', ['LTC-USD'])
        channel4 = Channel('ticker', ['LTC-USD'])
        
        self.assertIsNone(channel1 -  channel2)
        
        channel = channel1 - channel3
        self.assertEqual(channel.name, 'heartbeat')
        self.assertEqual(channel.product_ids, {'BTC-USD'})
        
        with self.assertRaises(TypeError):
            channel = channel1 - channel4


class TestClientProtocol(unittest.TestCase):
    """Tests for cbprotk.websocket.ClientProtocol"""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test__init__(self):
        pass
    
    def test___call__(self):
        prot = ClientProtocol()
        self.assertIs(prot(), prot)    
    

class TestClient(unittest.TestCase):
    """Tests for cbprotk.websocket.ClientProtocol"""

    def setUp(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()

    def test__init__(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        
        client = Client(self.loop, channel1, auto_connect=False)
        self.assertEqual(client._initial_channels, [channel1])
        self.assertEqual(client.feed_url, 'wss://ws-feed.pro.coinbase.com:443')
        
        client = Client(self.loop, channel1, SANDBOX_FEED_URL, auto_connect=False)
        self.assertEqual(client.feed_url, SANDBOX_FEED_URL)
        
        client = Client(self.loop, channel1, auto_connect=False)
        self.assertEqual(client._initial_channels, [channel1])
        self.assertEqual(client.channels, {channel1.name: channel1})
                              
        client = Client(self.loop, [channel1], auto_connect=False)
        self.assertEqual(client._initial_channels, [channel1])
        self.assertEqual(client.channels, {channel1.name: channel1})
        
        client = Client(self.loop, [channel1, channel2], auto_connect=False)
        self.assertEqual(client._initial_channels, [channel1, channel2])
        self.assertEqual(client.channels,
                         {channel1.name: channel1, channel2.name: channel2})
        
        client = Client(self.loop, [channel1, channel2], name="Test", auto_connect=False)
        self.assertEqual(client.name, "Test")
        
        #auth, no key, secret, or passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, channel1, auth=True, auto_connect=False)
            
        #auth, key, no secret or passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, channel1, auth=True, key='MyKey', auto_connect=False)
            
        #auth, key, secret, no passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, channel1, auth=True, key='MyKey',
                            secret='MySecret', auto_connect=False)
                            
        #auth, secret, no key or passphrase
        with self.assertRaises(ValueError):
            client = Client(self.loop, channel1, auth=True, secret='MySecret', auto_connect=False)
            
        #auth, secret, passphrase, no key
        with self.assertRaises(ValueError):
            client = Client(self.loop, channel1, auth=True, secret='MySecret',
                            passphrase='MyPassphrase', auto_connect=False)
                            
        #auth, passphrase, no key or secret
        with self.assertRaises(ValueError):
            client = Client(self.loop, channel1, auth=True, 
                            passphrase='MyPassphrase', auto_connect=False)
                            
        #auth, key, secret, passphrase
        client = Client(self.loop, channel1, auth=True, key='MyKey', 
                        secret='MySecret', passphrase='MyPassphrase', auto_connect=False)
        self.assertTrue(client.auth)
        self.assertEqual(client.key, 'MyKey')
        self.assertEqual(client.secret, 'MySecret')
        self.assertEqual(client.passphrase, 'MyPassphrase')
                        
    def test_get_subscribe_message(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        
        client = Client(self.loop, [channel1, channel2], auto_connect=False)
        msg = json.loads(client.get_subscribe_message(client.channels.values()).decode('utf8'))
        self.assertIn('type', msg)
        self.assertEqual(msg['type'], 'subscribe')
        self.assertIn('channels', msg)
        self.assertIn(channel1.as_dict(), msg['channels'])
        self.assertIn(channel2.as_dict(), msg['channels'])
        
    def test_subscribe(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        channel3 = Channel('heartbeat', ['BTC-USD', 'BTC-EUR'])
        
        client = Client(self.loop, [channel1], auto_connect=False)
        
        self.assertIn(channel1.name, client.channels)
        self.assertEqual(client.channels[channel1.name], channel1)
        
        client.subscribe(channel2)
        
        self.assertIn(channel2.name, client.channels)
        self.assertEqual(client.channels[channel2.name], channel2)
        
        client.subscribe(channel3)
        
        self.assertIn(channel3.name, client.channels)
        self.assertEqual(client.channels[channel3.name], channel1 + channel3)
        
    def test_unsubscribe(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD', 'LTC-EUR'])
        channel2 = Channel('level2', ['LTC-USD'])
        channel3 = Channel('heartbeat', ['LTC-EUR'])
        channel4 = Channel('heartbeat', ['BTC-USD', 'BTC-EUR'])
        channel5 = Channel('heartbeat', ['BCH-USD', 'LTC-USD'])
        
        client = Client(self.loop, [channel1, channel2], auto_connect=False)
        
        client.unsubscribe(channel3)
        
        self.assertIn(channel3.name, client.channels)
        self.assertEqual(client.channels[channel3.name], Channel('heartbeat', ['BTC-USD', 'LTC-USD']))
        
        client.unsubscribe(channel4)
        
        self.assertIn(channel4.name, client.channels)
        self.assertEqual(client.channels[channel4.name], Channel('heartbeat', ['LTC-USD']))
        
        client.unsubscribe(channel3)
        
        self.assertIn(channel3.name, client.channels)
        self.assertEqual(client.channels[channel3.name], Channel('heartbeat', ['LTC-USD']))
        
        client.unsubscribe(channel2)
        
        self.assertNotIn(channel2.name, client.channels)
        
        client.unsubscribe(channel5)
        
        self.assertEqual(client.channels, {})
        
        
        
        
        
        
        
        
        
        
        
