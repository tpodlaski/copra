#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `copra.websocket.channel` module."""

import unittest

from copra.websocket import Channel


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
            
    def test__as_dict(self):
        channel = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        d = channel._as_dict()
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
