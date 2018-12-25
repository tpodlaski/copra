#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Message` class.
"""

from asynctest import TestCase

from copra.message import Message

import pprint

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
        msg_dict[34] = '42'
        self.assertEqual(msg.dict, msg_dict)
        
        msg_dict[11] = 'my order id'
        msg_dict[34] = '69'
        msg_dict[35] = '8'
        msg_dict[150] = '0'
        
        msg = Message(TEST_KEY, 69, 8, {11: 'my order id', 150: '0'})
        self.assertEqual(msg.dict, msg_dict)

    
    def test___getitem__(self):
        msg = Message(TEST_KEY, 69, 8, {11: 'my order id', 150: '0'})
        self.assertEqual(msg[8], 'FIX.4.2')
        self.assertEqual(msg[35], '8')
        self.assertEqual(msg[49], TEST_KEY)
        self.assertEqual(msg[56], 'Coinbase')
        self.assertEqual(msg[34], '69')
        self.assertEqual(msg[11], 'my order id')
        self.assertEqual(msg[150], '0')
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


    def test___eq__(self):
        msg1 = Message(TEST_KEY, 0, 42)
        msg2 = Message(TEST_KEY, 0, 42)
        msg3 = Message(TEST_KEY, 0, 1972)
        
        self.assertEqual(msg1, msg2)
        self.assertNotEqual(msg1, msg3)


    def test___len__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(len(msg), 59)
        
        msg = Message(TEST_KEY, 42, 'A')
        self.assertEqual(len(msg), 59)
        
        msg = Message(TEST_KEY, 4200, 0)
        self.assertEqual(len(msg), 61)
        
        msg = Message(TEST_KEY, 69, 8, {11: 'my order id', 150: '0'})
        self.assertEqual(len(msg), 80)

 
    def test___repr__(self):
        msg = Message(TEST_KEY, 42, 0)
        pairs = repr(msg)[:-1].split(chr(1))
        keys = []
        for pair in pairs:
            key, value = pair.split('=')
            self.assertEqual(str(msg[int(key)]), value)
            keys.append(key)
        self.assertEqual(msg.dict.keys(), {int(key) for key in set(keys) - {'9', '10'}})
        self.assertEqual(keys[0], '8')
        self.assertEqual(keys[1], '9')
        self.assertEqual(keys[2], '35')

        
    def test___str__(self):
        msg = Message(TEST_KEY, 69, 8, {11: 'my order id', 150: '0'})
        msg_dict = msg.dict.copy()
        msg_dict[9] = msg[9]
        msg_dict[10] = msg[10]
        self.assertEqual(str(msg), pprint.pformat(msg_dict))


    def test___bytes__(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(bytes(msg), repr(msg).encode('ascii'))


    def test_checksum(self):
        msg = Message(TEST_KEY, 42, 0)
        self.assertEqual(msg.checksum(), '148')
        
    
    def test_from_formatted(self):
        msg = Message(TEST_KEY, 69, 8, {11: 'my order id', 150: '0'})
        
        msg2 = Message.from_formatted(repr(msg))
        self.assertEqual(msg2, msg)
        
        msg3 = Message.from_formatted(bytes(msg))
        self.assertEqual(msg3, msg)
        
        bad_cs = repr(msg)[:-2] + chr(1)
        with self.assertRaises(ValueError):
            msg4 = Message.from_formatted(bad_cs)
        