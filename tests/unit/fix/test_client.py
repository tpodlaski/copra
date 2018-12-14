#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Client` class.
"""

import asyncio
import os
import time

from asynctest import TestCase, CoroutineMock, MagicMock, patch

from copra.fix import Message, LoginMessage, LogoutMessage, HeartbeatMessage
from copra.fix import LimitOrderMessage, MarketOrderMessage
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
        
        
    def test___eq__(self):
        msg1 = Message(TEST_KEY, 0, 42)
        msg2 = Message(TEST_KEY, 0, 42)
        msg3 = Message(TEST_KEY, 0, 1972)
        
        self.assertEqual(msg1, msg2)
        self.assertNotEqual(msg1, msg3)


# class TestMessages(TestCase):
    
#     def test_LoginMessage(self):
#         msg = LoginMessage(TEST_KEY, TEST_SECRET, TEST_PASSPHRASE, 7, 
#                                                  send_time='1543883345.9289815')
#         self.assertEqual(msg[8], 'FIX.4.2')
#         self.assertEqual(msg[35], 'A')
#         self.assertEqual(msg[49], TEST_KEY)
#         self.assertEqual(msg[56], 'Coinbase')
#         self.assertEqual(msg[34], 7)
#         self.assertIn(52, msg)
#         self.assertEqual(msg[98], 0)
#         self.assertEqual(msg[108], 30)
#         self.assertEqual(msg[554], TEST_PASSPHRASE)
#         self.assertEqual(msg[8013], 'S')
#         self.assertEqual(msg[96], '6ps2fD4oRv/wwaXrP03ezMOZSmWt4FOEW1g2FoN2YNw=')


#     def test_LogoutMessage(self):
#         msg = LogoutMessage(TEST_KEY, 76)        
#         self.assertEqual(msg[8], 'FIX.4.2')
#         self.assertEqual(msg[35], '5')
#         self.assertEqual(msg[49], TEST_KEY)
#         self.assertEqual(msg[56], 'Coinbase')
#         self.assertEqual(msg[34], 76)
        
        
#     def test_HeartbeatMessage(self):
#         msg = HeartbeatMessage(TEST_KEY, 33)
#         self.assertEqual(msg[8], 'FIX.4.2')
#         self.assertEqual(msg[35], '0')
#         self.assertEqual(msg[49], TEST_KEY)
#         self.assertEqual(msg[56], 'Coinbase')
#         self.assertEqual(msg[34], 33)
#         with self.assertRaises(KeyError):
#             msg[112]
            
#         msg = HeartbeatMessage(TEST_KEY, 651, 2010)
#         self.assertEqual(msg[8], 'FIX.4.2')
#         self.assertEqual(msg[35], '0')
#         self.assertEqual(msg[49], TEST_KEY)
#         self.assertEqual(msg[56], 'Coinbase')
#         self.assertEqual(msg[34], 651)
#         self.assertEqual(msg[112], 2010)
        
        
#     def test_LimitOrderMessage(self):
        
#         base_dict = {8: 'FIX.4.2', 35: 'D', 49: TEST_KEY, 56: 'Coinbase', 22: 1}
        
#         # Limit buy order, defaults
#         msg = LimitOrderMessage(TEST_KEY, 7, 'buy', 'BTC-USD', 100, .001)
#         test_dict = {**base_dict,
#                      **{34: 7, 54: 2, 55: 'BTC-USD', 44: 100, 38: .001, 59: 1, 40: 2}} 
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Limit sell order, IOC time in force
#         msg = LimitOrderMessage(TEST_KEY, 101, 'sell', 'LTC-USD', 50, 2, 
#                                                       time_in_force='IOC')
#         test_dict = {**base_dict, 
#                      **{34: 101, 54: 1, 55: 'LTC-USD', 44: 50, 38:2, 59: 3, 40:2}}
#         self.assertEqual(test_dict.items(), msg.dict.items())

#         # Limit buy order, FOK time in force
#         msg = LimitOrderMessage(TEST_KEY, 93, 'buy', 'ETH-USD', 167, 5, 
#                                                     time_in_force='FOK')
#         test_dict = {**base_dict,
#                      **{34: 93, 54: 2, 55: 'ETH-USD', 44: 167, 38: 5, 59: 4, 40: 2}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Limit sell order, post only, client_oid
#         msg = LimitOrderMessage(TEST_KEY, 48, 'sell', 'BTC-USD', 1000, 1,
#                                       time_in_force='PO', client_oid='my_uuid')
#         test_dict = {**base_dict, 
#                      **{34: 48, 54: 1, 55: 'BTC-USD', 44: 1000, 38: 1, 59: 'P', 40: 2, 11: 'my_uuid'}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Stop limit buy order
#         msg = LimitOrderMessage(TEST_KEY, 3, 'buy', 'LTC-USD', 50, 3,
#                                                               stop_price=35)
#         test_dict = {**base_dict,
#                      **{34: 3, 54: 2, 55: 'LTC-USD', 44: 50, 38: 3, 59: 1, 40: 4, 99: 35}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Stop limit sell order
#         msg = LimitOrderMessage(TEST_KEY, 77, 'sell', 'ETH-USD', 15, 2.5,
#                                                                   stop_price=20)
#         test_dict = {**base_dict,
#                      **{34: 77, 54: 1, 55: 'ETH-USD', 44: 15, 38: 2.5, 59: 1, 40: 4, 99:20}}
#         self.assertEqual(test_dict.items(), msg.dict.items())


#     def test_MarketOrderMessage(self):
        
#         base_dict = {8: 'FIX.4.2', 35: 'D', 49: TEST_KEY, 56: 'Coinbase', 22: 1}
        
#         # Market buy order, size
#         msg = MarketOrderMessage(TEST_KEY, 1202, 'buy', 'BTC-USD', .002)
#         test_dict = {**base_dict,
#                      **{34: 1202, 54: 2, 55: 'BTC-USD', 38: .002, 40: 1}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Market buy order, funds
#         msg = MarketOrderMessage(TEST_KEY, 231, 'buy', 'LTC-USD', funds=1050)
#         test_dict = {**base_dict,
#                      **{34: 231, 54: 2, 55: 'LTC-USD', 152: 1050, 40: 1}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Market sell order, size
#         msg = MarketOrderMessage(TEST_KEY, 82, 'sell', 'BTC-USD', 3.5)
#         test_dict = {**base_dict,
#                      **{34: 82, 54: 1, 55: 'BTC-USD', 38: 3.5, 40: 1}}
#         self.assertEqual(test_dict.items(), msg.dict.items())            
        
#         # Market buy order, funds
#         msg = MarketOrderMessage(TEST_KEY, 14, 'buy', 'LTC-USD', funds=500)
#         test_dict = {**base_dict,
#                      **{34: 14, 54: 2, 55: 'LTC-USD', 152: 500, 40: 1}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Market sell order, funds
#         msg = MarketOrderMessage(TEST_KEY, 2, 'sell', 'ETH-USD', funds=200)
#         test_dict = {**base_dict,
#                      **{34: 2, 54: 1, 55: 'ETH-USD', 152: 200, 40: 1}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
#         # Stop market sell order, size, client_oid
#         msg = MarketOrderMessage(TEST_KEY, 65, 'sell', 'BTC-USD', .003,
#                                           stop_price=1500, client_oid='my_uuid')
#         test_dict = {**base_dict,
#                      **{34: 65, 54: 1, 55: 'BTC-USD', 38: .003, 40: 3, 99: 1500, 11: 'my_uuid'}}
#         self.assertEqual(test_dict.items(), msg.dict.items())
        
class TestFix(TestCase):
    
    # def setUp(self):
    #     pass
        
        
    # def tearDown(self):
    #     pass
    
    # async def test_constants(self):
    #     self.assertEqual(URL, 'fix.pro.coinbase.com:4198')
    #     self.assertEqual(SANDBOX_URL, 'fix-public.sandbox.pro.coinbase.com:4198')
    #     self.assertEqual(CERT_FILE, os.path.join(os.getcwd(), 
    #                                 'certs', 'fix.pro.coinbase.com.pem'))
    #     self.assertEqual(SANDBOX_CERT_FILE, 
    #                           os.path.join(os.getcwd(), 'certs', 
    #                           'fix-public.sandbox.pro.coinbase.com.pem'))


    # async def test_certs_exist(self):
    #     self.assertTrue(os.path.isfile(CERT_FILE))
    #     self.assertTrue(os.path.isfile(SANDBOX_CERT_FILE))      


    # async def test__init__(self):
        
    #     # Default host, port
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     self.assertEqual(client.loop, self.loop)
    #     self.assertEqual(client.key, TEST_KEY)
    #     self.assertEqual(client.secret, TEST_SECRET)
    #     self.assertEqual(client.passphrase, TEST_PASSPHRASE)
    #     self.assertEqual(client.url, 'fix.pro.coinbase.com:4198')
    #     self.assertEqual(client.host, 'fix.pro.coinbase.com')
    #     self.assertEqual(client.port, 4198)
    #     self.assertEqual(client.max_connect_attempts, 5)
    #     self.assertEqual(client.connect_timeout, 10)
    #     self.assertEqual(client.reconnect, True)
    #     self.assertEqual(client.seq_num, 0)
    #     self.assertFalse(client.connected.is_set())
    #     self.assertTrue(client.disconnected.is_set())
    #     self.assertFalse(client.logged_in.is_set())
    #     self.assertTrue(client.logged_out.is_set())
    #     self.assertFalse(client.is_closing)
    #     self.assertIsNone(client.keep_alive_task)
        
    #     # No defaults
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
    #                     url=SANDBOX_URL, cert_file=SANDBOX_CERT_FILE,
    #                     max_connect_attempts=3, connect_timeout=30, reconnect=False)
    #     self.assertEqual(client.loop, self.loop)
    #     self.assertEqual(client.key, TEST_KEY)
    #     self.assertEqual(client.secret, TEST_SECRET)
    #     self.assertEqual(client.passphrase, TEST_PASSPHRASE)
    #     self.assertEqual(client.url, 'fix-public.sandbox.pro.coinbase.com:4198')
    #     self.assertEqual(client.host, 'fix-public.sandbox.pro.coinbase.com')
    #     self.assertEqual(client.port, 4198)
    #     self.assertEqual(client.max_connect_attempts, 3)
    #     self.assertEqual(client.connect_timeout, 30)
    #     self.assertEqual(client.reconnect, False)
    #     self.assertEqual(client.seq_num, 0)
    #     self.assertFalse(client.connected.is_set())
    #     self.assertTrue(client.disconnected.is_set())
    #     self.assertFalse(client.logged_in.is_set())
    #     self.assertTrue(client.logged_out.is_set())
    #     self.assertFalse(client.is_closing)
    #     self.assertIsNone(client.keep_alive_task)


    # async def test___call__(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     self.assertEqual(client(), client)
        
        
    # def test_connection_lost(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.connected.set()
    #     client.logged_in.set()
    #     client.logged_out.clear()
    #     client.disconnected.clear()
        
    #     client.connection_lost()
        
    #     self.assertFalse(client.connected.is_set())
    #     self.assertFalse(client.logged_in.is_set())
    #     self.assertTrue(client.logged_out.is_set())
    #     self.assertTrue(client.disconnected.is_set())


    # async def test_data_received_logged_in(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     rec_msg = '35=A{}'.format(chr(1)).encode('ascii')
    #     client.data_received(rec_msg)
    #     self.assertTrue(client.logged_in.is_set())
    #     self.assertFalse(client.logged_out.is_set())
         
         
    # async def test_data_received_logged_out(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.logged_in.set()
    #     client.logged_out.clear()
    #     rec_msg = '35=5{}'.format(chr(1)).encode('ascii')
    #     client.data_received(rec_msg)
    #     self.assertFalse(client.logged_in.is_set())
    #     self.assertTrue(client.logged_out.is_set())
        
    
    # async def test_data_received_test(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.heartbeat = CoroutineMock()
    #     rec_msg = '35=1{}112=999{}'.format(chr(1), chr(1)).encode('ascii')
    #     client.data_received(rec_msg)
    #     client.heartbeat.assert_called_with('999')


    # async def test_connect_connect_attempts(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
    #                     url='example.com:1000', max_connect_attempts=3, connect_timeout=1)
                        
    #     client.loop.create_connection = CoroutineMock(side_effect=asyncio.TimeoutError)
    #     client.is_closing = True
    #     await client.connect()
    #     self.assertEqual(client.loop.create_connection.call_count, 3)
    #     self.assertFalse(client.is_closing)

        
    # async def test_connect_connect_timeout(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
    #                              url='example.com:1000', max_connect_attempts=1)
    #     client.is_closing = True
    #     start = time.time()
    #     await client.connect()
    #     duration = time.time() - start
    #     self.assertGreater(duration, 9.5)
    #     self.assertLess(duration, 10.5)
    #     self.assertFalse(client.is_closing)
        
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
    #                              url='example.com:1000', max_connect_attempts=1,
    #                              connect_timeout=5)
    #     start = time.time()
    #     await client.connect()
    #     duration = time.time() - start
    #     self.assertGreater(duration, 4.5)
    #     self.assertLess(duration, 5.5)

        
    # async def test_connect(self):
        
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE, reconnect=False)
    #     client.loop.create_connection = CoroutineMock(return_value=(None, None))
    #     client.login = CoroutineMock()
    #     client.keep_alive = CoroutineMock()
        
    #     def test():
    #         self.loop.create_connection.assert_called_with(client,
    #                                               'fix.pro.coinbase.com', 4198, 
    #                                               ssl=client.ssl_context)
    #         self.assertTrue(client.connected.is_set())
    #         self.assertFalse(client.disconnected.is_set())
    #         client.login.assert_called()
    #         client.keep_alive.assert_called()
    #         self.assertFalse(client.is_closing)
            
    #         client.is_closing = True
    #         client.connection_lost()

    #     self.loop.call_later(1, test)

    #     await client.connect()
        
        
    # async def test_connect_reconnect(self):
        
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.loop.create_connection = CoroutineMock(return_value=(None, None))
    #     client.login = CoroutineMock()
    #     client.keep_alive = CoroutineMock()

    #     def test():
    #         self.loop.create_connection.assert_called_with(client,
    #                                               'fix.pro.coinbase.com', 4198, 
    #                                               ssl=client.ssl_context)
    #         self.assertTrue(client.connected.is_set())
    #         self.assertFalse(client.disconnected.is_set())
    #         client.login.assert_called()
    #         client.keep_alive.assert_called()
    #         self.assertFalse(client.is_closing)
            
    #         client.connection_lost()
            
    #         self.loop.call_later(1, test2)
            
    #     def test2():
    #         self.loop.create_connection.assert_called_with(client,
    #                                               'fix.pro.coinbase.com', 4198, 
    #                                               ssl=client.ssl_context)
    #         self.assertEqual(self.loop.create_connection.call_count, 2)
    #         self.assertTrue(client.connected.is_set())
    #         self.assertFalse(client.disconnected.is_set())
    #         client.login.assert_called()
    #         client.keep_alive.assert_called()
    #         self.assertFalse(client.is_closing)
            
    #         client.is_closing = True
    #         client.connection_lost()            
            

    #     self.loop.call_later(1, test)        

    #     await client.connect()


    # async def test_close(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     self.assertFalse(client.connected.is_set())
    #     self.assertTrue(client.disconnected.is_set())
    
    #     # Fake a connect()
    #     client.transport = MagicMock()
    #     client.transport.close = MagicMock(side_effect=client.connection_lost)
    #     client.connected.set()
    #     client.disconnected.clear()
    #     client.logged_in.set()
    #     client.logged_out.clear()
    #     client.is_closing = False
        
    #     await client.close()
    #     client.transport.close.assert_called()
    #     self.assertFalse(client.connected.is_set())
    #     self.assertTrue(client.disconnected.is_set())
    #     self.assertFalse(client.logged_in.is_set())
    #     self.assertTrue(client.logged_out.is_set())
    #     client.is_closing = True
        
        
    # async def test_send(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.transport = MagicMock()
    #     client.transport.write = MagicMock()
        
    #     msg = LogoutMessage(TEST_KEY, 35)
    #     await client.send(msg)
        
    #     client.transport.write.assert_called_with(bytes(msg))

        
    # async def test_login(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.transport = MagicMock()
    #     rec_msg = '35=A{}'.format(chr(1)).encode('ascii')
    #     client.transport.write = MagicMock(side_effect=lambda x: client.data_received(rec_msg))
        
    #     msg = LoginMessage(TEST_KEY, TEST_SECRET, TEST_PASSPHRASE, 1, 
    #                                              send_time='1543883345.9289815')
        
    #     self.assertEqual(client.seq_num, 0)
    #     await client.login(send_time='1543883345.9289815')
        
    #     client.transport.write.assert_called_with(bytes(msg))
    #     self.assertEqual(client.seq_num, 1)
    #     self.assertTrue(client.logged_in.is_set())
    #     self.assertFalse(client.logged_out.is_set())
        
        
    # async def test_logout(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.transport = MagicMock()
    #     rec_msg = '35=5{}'.format(chr(1)).encode('ascii')
    #     client.transport.write = MagicMock(side_effect=lambda x: client.data_received(rec_msg))
        
    #     client.logged_in.set()
    #     client.logged_out.clear()
    
    #     self.assertEqual(client.seq_num, 0)
    #     await client.logout()
        
    #     client.transport.write.assert_called_with(bytes(LogoutMessage(TEST_KEY, 1)))
    #     self.assertEqual(client.seq_num, 1)
    #     self.assertFalse(client.logged_in.is_set())
    #     self.assertTrue(client.logged_out.is_set())
        
        
    # async def test_heartbeat(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.transport = MagicMock()
    #     client.transport.write = MagicMock()
        
    #     self.assertEqual(client.seq_num, 0)
    #     await client.heartbeat()
        
    #     client.transport.write.assert_called_with(bytes(HeartbeatMessage(TEST_KEY, 1)))
    #     self.assertEqual(client.seq_num, 1)
        
    #     await client.heartbeat(333)
        
    #     client.transport.write.assert_called_with(bytes(HeartbeatMessage(TEST_KEY, 2, 333)))
    #     self.assertEqual(client.seq_num, 2)
        
        
    # async def test_keep_alive(self):
    #     client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    #     client.transport = MagicMock()
    #     client.transport.write = MagicMock()
    #     client.logged_in.set()
    #     client.logged_out.clear()
        
    #     self.loop.create_task(client.keep_alive(2))
        
    #     await asyncio.sleep(10)
    #     client.logged_out.set()
    #     client.logged_in.clear()
        
    #     self.assertGreater(client.transport.write.call_count, 3)
    #     client.transport.write.assert_any_call(bytes(HeartbeatMessage(TEST_KEY, 1)))
    
    async def test_market_order(self):
        
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.send = CoroutineMock()
        
        # Invalid side
        with self.assertRaises(ValueError):
            resp = await client.market_order('dark', 'BTC-USD', .001)
        
        # No funds or size
        with self.assertRaises(ValueError):
            resp = await client.market_order('buy', 'BTC-USD')
            
        # funds and size
        with self.assertRaises(ValueError):
            resp = await client.market_order('buy', 'BTC-USD', size=.001, funds=10000)
                                               
        # size, client_oid
        expected = MarketOrderMessage(TEST_KEY, client.seq_num+1, 'buy', 
                                            'BTC-USD', .001, client_oid='my_uuid')
        resp = await client.market_order('buy', 'BTC_USD', .001, 
                                                client_oid='my_uuid')
        

        # # Size, client_oid, stp
        # resp = await self.auth_client.market_order('buy', 'BTC-USD', size=3,
        #                                         client_oid='Order 66', stp='co')
        # self.check_req(self.mock_post, '{}/orders'.format(URL),
        #               data={'side': 'buy', 'product_id': 'BTC-USD',
        #                   'type': 'market', 'size': 3, 'client_oid': 'Order 66', 
        #                   'stp': 'co'},
        #               headers=AUTH_HEADERS)
                      
        # # Funds, no client_oid, default stp
        # resp = await self.auth_client.market_order('buy', 'BTC-USD', funds=500)
        # self.check_req(self.mock_post, '{}/orders'.format(URL),
        #               data={'side': 'buy', 'product_id': 'BTC-USD',
        #                     'type': 'market', 'funds': 500, 'stp': 'dc'},
        #               headers=AUTH_HEADERS)

        # # Funds, client_oid, stp
        # resp = await self.auth_client.market_order('buy', 'BTC-USD', funds=300,
        #                                      client_oid='of the Jedi', stp='cb')
        # self.check_req(self.mock_post, '{}/orders'.format(URL),
        #               data={'side': 'buy', 'product_id': 'BTC-USD',
        #                   'type': 'market', 'funds': 300, 
        #                   'client_oid': 'of the Jedi', 'stp': 'cb'},
        #               headers=AUTH_HEADERS)
        