#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Client` class.
"""

import asyncio
import os

from asynctest import TestCase, CoroutineMock

from copra.fix import Message
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

class TestFix(TestCase):
    
    def setUp(self):
        self.client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    
    def tearDown(self):
        pass
    
    async def test_constants(self):
        self.assertEqual(URL, 'fix.pro.coinbase.com:4198')
        self.assertEqual(SANDBOX_URL, 'fix-public.sandbox.pro.coinbase.com')
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
        self.assertEqual(client.url, URL)
        self.assertEqual(client.seq_num, 0)


    async def test_connect(self):
        
        self.loop.create_connection = CoroutineMock(name='create_connection')
        await self.client.connect()
        self.loop.create_connection.assert_called_with(self.client,
                                                   'fix.pro.coinbase.com', 4198, 
                                                   ssl=self.client.ssl_context)
        