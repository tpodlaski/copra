#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cbprotk.websocket` module."""

import asyncio
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
            
    def test___call__(self):
        channel = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        self.assertIs(channel(), channel)
            
    def test_as_dict(self):
        channel = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        d = channel.as_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['name'], 'heartbeat')
        self.assertEqual(len(d['product_ids']), 2)
        self.assertIn('BTC-USD', d['product_ids'])
        self.assertIn('LTC-USD', d['product_ids'])
        

class TestClientProtocol(unittest.TestCase):
    """Tests for cbprotk.websocket.ClientProtocol"""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test__init__(self):
        pass
    

class TestClient(unittest.TestCase):
    """Tests for cbprotk.websocket.ClientProtocol"""

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()

    def test__init__(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        
        client = Client(self.loop, channel1)
        self.assertEqual(client._initial_channels, [channel1])
        self.assertEqual(client.feed_url, 'wss://ws-feed.gdax.com')
        
        client = Client(self.loop, channel1, SANDBOX_FEED_URL)
        self.assertEqual(client.feed_url, SANDBOX_FEED_URL)
        
        client = Client(self.loop, [channel1])
        self.assertEqual(client._initial_channels, [channel1])
        
        client = Client(self.loop, [channel1, channel2])
        self.assertEqual(client._initial_channels, [channel1, channel2])