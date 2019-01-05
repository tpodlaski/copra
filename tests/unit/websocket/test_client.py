#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `copra.websocket` module."""

import asyncio
import json
import sys
from urllib.parse import urlparse

from asynctest import TestCase, patch, CoroutineMock, MagicMock, skipUnless

from copra.websocket import Channel, Client, FEED_URL, SANDBOX_FEED_URL
from copra.websocket.client import ClientProtocol

# These are made up
TEST_KEY = 'a035b37f42394a6d343231f7f772b99d'
TEST_SECRET = 'aVGe54dHHYUSudB3sJdcQx4BfQ6K5oVdcYv4eRtDN6fBHEQf5Go6BACew4G0iFjfLKJHmWY5ZEwlqxdslop4CC=='
TEST_PASSPHRASE = 'a2f9ee4dx2b'


class TestClientProtocol(TestCase):
    """Tests for cbprotk.websocket.ClientProtocol"""

    def setUp(self):
        self.protocol = ClientProtocol()
        self.protocol.factory = MagicMock()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test___call__(self):
        self.assertIs(self.protocol(), self.protocol)
        
    @skipUnless(sys.version_info >= (3, 6), 'MagicMock.assert_called_once not implemented.')
    def test_onOpen(self):
        self.protocol.onOpen()
        self.protocol.factory.on_open.assert_called_once()
    
    def test_onClose(self):
        self.protocol.onClose(True, 200, 'OK')
        self.protocol.factory.on_close.assert_called_with(True, 200, 'OK')
        
    def test_onMessage(self):
        msg_dict = {'type': 'test', 'another_key': 200}
        msg = json.dumps(msg_dict).encode('utf8')
        self.protocol.onMessage(msg, True)
        self.protocol.factory.on_message.assert_called_with(msg_dict)
        
        msg_dict = {'type': 'error', 'message': 404, 'reason': 'testing'}
        msg = json.dumps(msg_dict).encode('utf8')
        self.protocol.onMessage(msg, True)
        self.protocol.factory.on_error.called_with(404, 'testing')
        

class TestClient(TestCase):
    """Tests for copra.websocket.client.Client"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
        client = Client(self.loop, channel1, auth=True, key=TEST_KEY, 
                        secret=TEST_SECRET, passphrase=TEST_PASSPHRASE, 
                        auto_connect=False, auto_reconnect=False)
        self.assertEqual(client.loop, self.loop)
        self.assertEqual(client._initial_channels, [channel1])
        self.assertEqual(client.feed_url, FEED_URL)
        self.assertEqual(client.channels, {channel1.name: channel1})
        self.assertTrue(client.auth)
        self.assertEqual(client.key, TEST_KEY)
        self.assertEqual(client.secret, TEST_SECRET)
        self.assertEqual(client.passphrase, TEST_PASSPHRASE)
        self.assertFalse(client.auto_connect)
        self.assertFalse(client.auto_reconnect)
        self.assertEqual(client.name, 'WebSocket Client')
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.closing)

    @skipUnless(sys.version_info >= (3, 6), 'MagicMock.assert_called_once not implemented.')
    def test__init__auto_connect(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
    
        #noauth, auto_connect, name
        with patch('copra.websocket.client.Client.add_as_task_to_loop') as mock_attl:
            client = Client(self.loop, channel1, name="Custom Name")
            self.assertEqual(client.loop, self.loop)
            self.assertEqual(client._initial_channels, [channel1])
            self.assertEqual(client.feed_url, FEED_URL)
            self.assertEqual(client.channels, {channel1.name: channel1})
            self.assertFalse(client.auth)
            self.assertTrue(client.auto_connect)
            self.assertTrue(client.auto_reconnect)
            self.assertEqual(client.name, 'Custom Name')
            self.assertFalse(client.connected.is_set())
            self.assertTrue(client.disconnected.is_set())
            self.assertFalse(client.closing)
            mock_attl.assert_called_once()
        
                        
    def test__get_subscribe_message(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        
        client = Client(self.loop, [channel1, channel2], auto_connect=False)
        #subscribe
        msg = json.loads(client._get_subscribe_message(client.channels.values()).decode('utf8'))
        self.assertEqual(len(msg), 2)
        self.assertEqual(msg['type'], 'subscribe')
        self.assertIn(channel1._as_dict(), msg['channels'])
        self.assertIn(channel2._as_dict(), msg['channels'])
        #unsubscribe
        msg = json.loads(client._get_subscribe_message([channel1], unsubscribe=True).decode('utf8'))
        self.assertEqual(len(msg), 2)
        self.assertEqual(msg['type'], 'unsubscribe')
        self.assertIn(channel1._as_dict(), msg['channels'])
        self.assertFalse(channel2._as_dict() in  msg['channels'])

        #authorized
        client = Client(self.loop, channel1, auth=True, key=TEST_KEY, 
                        secret=TEST_SECRET, passphrase=TEST_PASSPHRASE, 
                        auto_connect=False, auto_reconnect=False)
                        
        msg = json.loads(client._get_subscribe_message(client.channels.values(), 
                                 timestamp='1546384260.0321212').decode('utf8'))
        self.assertEqual(len(msg), 6)
        self.assertEqual(msg['type'], 'subscribe')
        self.assertIn(channel1._as_dict(), msg['channels'])
        self.assertEqual(msg['key'], TEST_KEY)
        self.assertEqual(msg['passphrase'], TEST_PASSPHRASE)
        self.assertEqual(msg['timestamp'], '1546384260.0321212')
        self.assertEqual(msg['signature'], 'KQq/poDCHjDDRURkQOc+QZi16c6cio9Yo/nF1+kts84=')

                        
    def test_subscribe(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        channel2 = Channel('level2', ['LTC-USD'])
        channel3 = Channel('heartbeat', ['BTC-USD', 'BTC-EUR'])
        channel4 = Channel('heartbeat', ['ETH-USD'])
        
        client = Client(self.loop, [channel1], auto_connect=False)
        
        self.assertIn(channel1.name, client.channels)
        self.assertEqual(client.channels[channel1.name], channel1)
        
        client.subscribe(channel2)
        
        self.assertIn(channel2.name, client.channels)
        self.assertEqual(client.channels[channel2.name], channel2)
        
        client.subscribe(channel3)
    
        self.assertIn(channel3.name, client.channels)
        self.assertEqual(client.channels[channel3.name], channel1 + channel3)
        
        client.protocol.sendMessage = MagicMock()
        client.connected.set()
        
        client.subscribe(channel4)
 
        msg = client._get_subscribe_message([channel4])
        client.protocol.sendMessage.assert_called_with(msg)

        
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
        
        client.protocol.sendMessage = MagicMock()
        client.connected.set()
        
        client.unsubscribe(channel5)
        self.assertEqual(client.channels, {})
        msg = client._get_subscribe_message([channel5], unsubscribe=True)
        client.protocol.sendMessage.assert_called_with(msg)

    
    def test_add_as_task_to_loop(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD'])
        client = Client(self.loop, channel1, auto_connect=False)
        
        client.loop.create_connection = CoroutineMock(return_value=CoroutineMock())
        client.add_as_task_to_loop()
        
        url = urlparse(FEED_URL)
        client.loop.create_connection.assert_called_with(client, url.hostname, url.port, ssl=True)

        
    def test_on_open(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD', 'LTC-EUR'])
        channel2 = Channel('level2', ['LTC-USD'])
        client = Client(self.loop, [channel1, channel2], auto_connect=False)
        client.protocol.sendMessage = MagicMock()
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.closing)
        
        msg = client._get_subscribe_message(client.channels.values())
        client.on_open()
        
        self.assertTrue(client.connected.is_set())
        self.assertFalse(client.disconnected.is_set())
        self.assertFalse(client.closing)
        client.protocol.sendMessage.assert_called_with(msg)

       
    def test_on_close(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD', 'LTC-EUR'])
        client = Client(self.loop, [channel1], auto_connect=False)
        client.add_as_task_to_loop = MagicMock()
        client.connected.set()
        client.disconnected.clear()
        client.closing = True
        
        client.on_close(True, None, None)
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertTrue(client.closing)
        client.add_as_task_to_loop.assert_not_called()
    
    @skipUnless(sys.version_info >= (3, 6), 'MagicMock.assert_called_once not implemented.')
    def test_on_close_unexpected(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD', 'LTC-EUR'])
        client = Client(self.loop, [channel1], auto_connect=False)
        client.add_as_task_to_loop = MagicMock()
        
        client.connected.set()
        client.disconnected.clear()
        client.closing = False
        
        client.on_close(True, None, None)
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.closing)
        client.add_as_task_to_loop.assert_called_once()
        
        
    @skipUnless(sys.version_info >= (3, 6), 'MagicMock.assert_called_once not implemented. ')   
    async def test_close(self):
        channel1 = Channel('heartbeat', ['BTC-USD', 'LTC-USD', 'LTC-EUR'])
        client = Client(self.loop, [channel1], auto_connect=False)
        client.protocol.sendClose = MagicMock(side_effect=lambda: client.disconnected.set())
        client.disconnected.clear()
        self.assertFalse(client.closing)
        
        await client.close()
        self.assertTrue(client.closing)
        client.protocol.sendClose.assert_called_once()
        
        