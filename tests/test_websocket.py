#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cbprotk.websocket` module."""


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
        self.assertIsInstance(channel.product_ids, list)
        self.assertEqual(channel.product_ids, ['BTC-USD'])
        
        #product_ids as list length 1
        channel = Channel('heartbeat', ['BTC-USD'])
        self.assertIsInstance(channel.product_ids, list)
        self.assertEqual(channel.product_ids, ['BTC-USD'])
        
        #product_ids as list length 2
        channel = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        self.assertIsInstance(channel.product_ids, list)
        self.assertEqual(channel.product_ids, ['BTC-USD', 'LTC-USD'])
        
        #empty product_ids string
        with self.assertRaises(ValueError):
            channel = Channel('heartbeat', '')
            
        #empty product_ids list
        with self.assertRaises(ValueError):
            channel = Channel('heartbeat', [])        
        
        