#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `copra.websocket` module."""

import asyncio
import json
import unittest

from copra.websocket.channel import Channel
from copra.websocket.client import ClientProtocol, Client, SANDBOX_FEED_URL


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
                        
    def test__get_subscribe_message(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        
        client = Client(self.loop, [channel1, channel2], auto_connect=False)
        msg = json.loads(client._get_subscribe_message(client.channels.values()).decode('utf8'))
        self.assertIn('type', msg)
        self.assertEqual(msg['type'], 'subscribe')
        self.assertIn('channels', msg)
        self.assertIn(channel1._as_dict(), msg['channels'])
        self.assertIn(channel2._as_dict(), msg['channels'])
        
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
        
        
        
        
        
        
        
        
        
        
        
