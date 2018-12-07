#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Client` class.
"""

import asyncio
import os

from asynctest import TestCase, CoroutineMock, MagicMock, patch

from copra.fix import Message, LoginMessage, LogoutMessage
from copra.fix import Client, URL, SANDBOX_URL, CERT_FILE, SANDBOX_CERT_FILE

# These are made up
TEST_KEY = 'a035b37f42394a6d343231f7f772b99d'
TEST_SECRET = 'aVGe54dHHYUSudB3sJdcQx4BfQ6K5oVdcYv4eRtDN6fBHEQf5Go6BACew4G0iFjfLKJHmWY5ZEwlqxdslop4CC=='
TEST_PASSPHRASE = 'a2f9ee4dx2b'


class TestMessage(TestCase):
    
    def test___init__(self):
        
        msg_dict = { 8: 'FIX.4.2',
             35: '0',
             49: TEST_KEY,
             56: 'Coinbase',
             34: 42 }
             
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(msg.dict, msg_dict)
    
        
    def test___len__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(len(msg), 59)
        
        msg = Message(TEST_KEY, 42, 'A')
        self.assertEqual(len(msg), 59)
        
        msg = Message(TEST_KEY, 4200, 0)
        self.assertEqual(len(msg), 61)


    def test___repr__(self):
        msg = Message(TEST_KEY, 42, 0)
        pairs = str(msg)[:-1].split(chr(1))
        keys = []
        for pair in pairs:
            key, value = pair.split('=')
            self.assertEqual(str(msg[int(key)]), value)
            keys.append(key)
        self.assertEqual(msg.dict.keys(), {int(key) for key in set(keys) - {'9', '10'}})
        self.assertEqual(keys[0], '8')
        self.assertEqual(keys[1], '9')
        self.assertEqual(keys[2], '35')

        
    def test_checksum(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(msg.checksum(), '148')
        
        
    def test___bytes__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(bytes(msg), msg.__repr__().encode('ascii'))


    def test___getitem__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(msg[8], 'FIX.4.2')
        self.assertEqual(msg[35], '0')
        self.assertEqual(msg[49], TEST_KEY)
        self.assertEqual(msg[56], 'Coinbase')
        self.assertEqual(msg[34], 42)
        self.assertEqual(msg[9], len(msg))
        self.assertEqual(msg[10], msg.checksum())

        
    def test___setitem__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(msg[35], '0')
        
        msg[35] = 'A'
        self.assertEqual(msg[35], 'A')
        
        with self.assertRaises(KeyError):
            t = msg[99]
        msg[99] = 'hello'
        self.assertEqual(msg[99], 'hello')
        
        with self.assertRaises(KeyError):
            msg[9] = 'nine'
            
        with self.assertRaises(KeyError):
            msg[10] = 'ten'
        

    def test___delitem__(self):
        msg = Message(TEST_KEY, 42, 0)
        del(msg[35])
        with self.assertRaises(KeyError):
            t = msg[35]
            
        with self.assertRaises(KeyError):
            del(msg[99])
            
            
    def test___contains__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertTrue(msg.__contains__(8))
        self.assertTrue(msg.__contains__(9))
        self.assertTrue(msg.__contains__(10))
        self.assertFalse(msg.__contains__(99))
        
        self.assertIn(8, msg)
        self.assertIn(9, msg)
        self.assertIn(10, msg)
        self.assertNotIn(99, msg)


class TestMessages(TestCase):
    
    def test_LoginMessage(self):
        msg = LoginMessage(TEST_KEY, TEST_SECRET, TEST_PASSPHRASE, 7, 
                                                 send_time='1543883345.9289815')
        self.assertEqual(msg[8], 'FIX.4.2')
        self.assertEqual(msg[35], 'A')
        self.assertEqual(msg[49], TEST_KEY)
        self.assertEqual(msg[56], 'Coinbase')
        self.assertEqual(msg[34], 7)
        self.assertIn(52, msg)
        self.assertEqual(msg[98], 0)
        self.assertEqual(msg[108], 30)
        self.assertEqual(msg[554], TEST_PASSPHRASE)
        self.assertEqual(msg[8013], 'S')
        self.assertEqual(msg[96], '6ps2fD4oRv/wwaXrP03ezMOZSmWt4FOEW1g2FoN2YNw=')


    def test_LogoutMessage(self):
        msg = LogoutMessage(TEST_KEY, 76)        
        self.assertEqual(msg[8], 'FIX.4.2')
        self.assertEqual(msg[35], '5')
        self.assertEqual(msg[49], TEST_KEY)
        self.assertEqual(msg[56], 'Coinbase')
        self.assertEqual(msg[34], 76)


class TestFix(TestCase):
    
    def setUp(self):
        pass
        
        
    def tearDown(self):
        pass
    
    async def test_constants(self):
        self.assertEqual(URL, 'fix.pro.coinbase.com:4198')
        self.assertEqual(SANDBOX_URL, 'fix-public.sandbox.pro.coinbase.com:4198')
        self.assertEqual(CERT_FILE, os.path.join(os.getcwd(), 
                                    'certs', 'fix.pro.coinbase.com.pem'))
        self.assertEqual(SANDBOX_CERT_FILE, 
                               os.path.join(os.getcwd(), 'certs', 
                              'fix-public.sandbox.pro.coinbase.com.pem'))


    async def test_certs_exist(self):
        self.assertTrue(os.path.isfile(CERT_FILE))
        self.assertTrue(os.path.isfile(SANDBOX_CERT_FILE))      


    async def test__init__(self):
        
        # Default host, port
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        self.assertEqual(client.loop, self.loop)
        self.assertEqual(client.key, TEST_KEY)
        self.assertEqual(client.secret, TEST_SECRET)
        self.assertEqual(client.passphrase, TEST_PASSPHRASE)
        self.assertEqual(client.url, 'fix.pro.coinbase.com:4198')
        self.assertEqual(client.host, 'fix.pro.coinbase.com')
        self.assertEqual(client.port, 4198)
        self.assertEqual(client.seq_num, 0)


    async def test___call__(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        self.assertEqual(client(), client)


    async def test_connect(self):
        
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.loop.create_connection = CoroutineMock(return_value=(None, None))
        
        await client.connect()
        self.loop.create_connection.assert_called_with(client,
                                                  'fix.pro.coinbase.com', 4198, 
                                                  ssl=client.ssl_context)
        self.assertTrue(client.connected.is_set())
        self.assertFalse(client.disconnected.is_set())


    async def test_close(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        self.assertTrue(client.disconnected.is_set())
    
        # Fake a connect()
        client.transport = MagicMock()
        client.transport.close = MagicMock(side_effect=client.connection_lost)
        client.connected.set()
        client.disconnected.clear()
        
        await client.close()
        client.transport.close.assert_called()
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        
        
    async def test_send(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.transport = MagicMock()
        client.transport.write = MagicMock()
        
        msg = LogoutMessage(TEST_KEY, 35)
        await client.send(msg)
        
        client.transport.write.assert_called_with(bytes(msg))

        
    async def test_login(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.transport = MagicMock()
        rec_msg = '35=A{}'.format(chr(1)).encode('ascii')
        client.transport.write = MagicMock(side_effect=lambda x: client.data_received(rec_msg))
        
        msg = LoginMessage(TEST_KEY, TEST_SECRET, TEST_PASSPHRASE, 1, 
                                                 send_time='1543883345.9289815')
        
        self.assertEqual(client.seq_num, 0)
        await client.login(send_time='1543883345.9289815')
        
        client.transport.write.assert_called_with(bytes(msg))
        self.assertEqual(client.seq_num, 1)
        self.assertTrue(client.logged_in.is_set())
        self.assertFalse(client.logged_out.is_set())
        
        
    async def test_logout(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.transport = MagicMock()
        rec_msg = '35=5{}'.format(chr(1)).encode('ascii')
        client.transport.write = MagicMock(side_effect=lambda x: client.data_received(rec_msg))
        
        client.logged_in.set()
        client.logged_out.clear()
    
        self.assertEqual(client.seq_num, 0)
        await client.logout()
        
        client.transport.write.assert_called_with(bytes(LogoutMessage(TEST_KEY, 1)))
        self.assertEqual(client.seq_num, 1)
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
        