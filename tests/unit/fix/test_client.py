#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Client` class.
"""

import asyncio
from decimal import Decimal
import os
import random
import time
import uuid

from asynctest import TestCase, CoroutineMock, MagicMock, patch

from copra.fix import Client, URL, SANDBOX_URL, CERT_FILE, SANDBOX_CERT_FILE
from copra.message import Message
from copra.order import Order

# These are made up
TEST_KEY = 'a035b37f42394a6d343231f7f772b99d'
TEST_SECRET = 'aVGe54dHHYUSudB3sJdcQx4BfQ6K5oVdcYv4eRtDN6fBHEQf5Go6BACew4G0iFjfLKJHmWY5ZEwlqxdslop4CC=='
TEST_PASSPHRASE = 'a2f9ee4dx2b'


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
        self.assertEqual(client.max_connect_attempts, 5)
        self.assertEqual(client.connect_timeout, 10)
        self.assertEqual(client.reconnect, True)
        self.assertEqual(client.seq_num, 0)
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
        self.assertFalse(client.is_closing)
        self.assertIsNone(client.keep_alive_task)
        self.assertIsInstance(client.orders, dict)
        self.assertEqual(len(client.orders), 0)
        
        # No defaults
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
                        url=SANDBOX_URL, cert_file=SANDBOX_CERT_FILE,
                        max_connect_attempts=3, connect_timeout=30, reconnect=False)
        self.assertEqual(client.loop, self.loop)
        self.assertEqual(client.key, TEST_KEY)
        self.assertEqual(client.secret, TEST_SECRET)
        self.assertEqual(client.passphrase, TEST_PASSPHRASE)
        self.assertEqual(client.url, 'fix-public.sandbox.pro.coinbase.com:4198')
        self.assertEqual(client.max_connect_attempts, 3)
        self.assertEqual(client.connect_timeout, 30)
        self.assertEqual(client.reconnect, False)
        self.assertEqual(client.seq_num, 0)
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
        self.assertFalse(client.is_closing)
        self.assertIsNone(client.keep_alive_task)
        self.assertIsInstance(client.orders, dict)
        self.assertEqual(len(client.orders), 0)
        
        
    async def test_host(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        self.assertEqual(client.host, 'fix.pro.coinbase.com')
        
        
    async def test_port(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        self.assertEqual(client.port, 4198)
        
        
    async def test___call__(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        self.assertEqual(client(), client)
        
        
    async def test_connection_made(self):
        pass
        
    
    def test_connection_lost(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        
        client.connected.set()
        client.logged_in.set()
        client.logged_out.clear()
        client.disconnected.clear()
        
        client.connection_lost()
        
        self.assertFalse(client.connected.is_set())
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
        self.assertTrue(client.disconnected.is_set())
    
    
    async def test_data_received_logged_in(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.logged_in.clear()
        client.logged_out.set()
        resp_msg = Message(TEST_KEY, 109, 'A')
        client.data_received(bytes(resp_msg))
        self.assertTrue(client.logged_in.is_set())
        self.assertFalse(client.logged_out.is_set())
        
        
    async def test_data_received_logged_out(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.logged_in.set()
        client.logged_out.clear()
        resp_msg = Message(TEST_KEY, 109, '5')
        client.data_received(bytes(resp_msg))
        self.assertFalse(client.logged_in.is_set())
        
        
    async def test_data_received_test(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.heartbeat = CoroutineMock()
        resp_msg = Message(TEST_KEY, 45, '1', {112: '999'})
        client.data_received(bytes(resp_msg))
        client.heartbeat.assert_called_with('999')


    def test_data_received_exec_report(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        order, _ = Order.market_order(TEST_KEY, 1, 'buy', 'BTC-USD', .001)
        order.fix_update = MagicMock()
        client.orders[order.client_oid] = order
        msg = Message(TEST_KEY, 69, 8, {37: str(uuid.uuid4()), 39:0, 150: 0, 
                                                          11: order.client_oid})
        client.data_received(bytes(msg))
        order.fix_update.assert_called_with(msg)
        
    
    async def test_data_received_exec_report_new(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.send = MagicMock()
        self.assertEqual(len(client.orders), 0)
        order, _ = Order.market_order(TEST_KEY, client.seq_num, 'buy', 'BTC-USD', .001)
        client.orders[order.client_oid] = order
        self.assertIsNone(order.id)
        self.assertIsNone(order.status)
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        assigned_id = str(uuid.uuid4())
        msg = Message(TEST_KEY, 2, 8, {11: order.client_oid, 37: assigned_id, 39: '0', 150: '0'})
        client.data_received(bytes(msg))
        
        self.assertIn(assigned_id, client.orders)
        self.assertEqual(order.id, assigned_id)
        self.assertEqual(order.status, 'new')
        self.assertTrue(order.received.is_set())
        self.assertFalse(order.done.is_set())


    async def test_data_received_exec_report_rejected(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.send = MagicMock()
        self.assertEqual(len(client.orders), 0)
        order, _ = Order.market_order(TEST_KEY, client.seq_num, 'buy', 'BTC-USD', .001)
        client.orders[order.client_oid] = order
        self.assertIsNone(order.id)
        self.assertIsNone(order.status)
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        assigned_id = str(uuid.uuid4())
        msg = Message(TEST_KEY, 2, 8, {11: order.client_oid, 37: assigned_id, 39: '8', 150: '8', 58: 'TOO LATE'})
        client.data_received(bytes(msg))
        
        self.assertIn(assigned_id, client.orders)
        self.assertEqual(order.id, assigned_id)
        self.assertEqual(order.status, 'rejected')
        self.assertEqual(order.reject_reason, 'TOO LATE')
        self.assertTrue(order.received.is_set())
        self.assertTrue(order.done.is_set())
        
    async def test_data_received_exec_report_fill(self):
        def receive_order(self, msg):
            assigned_id = str(uuid.uuid4())
            rec_msg = Message(TEST_KEY, 2, 8, {11: msg[11], 37: assigned_id,
                                                             39: '0', 150: '0'})
            self.data_received(bytes(rec_msg))
        
        with patch.object(Client, 'send', autospec=True, side_effect=receive_order):
       
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
            order = await client.market_order('buy', 'BTC-USD', 1)
        
            self.assertEqual(order.status, 'new')
            self.assertEqual(order.filled_size, Decimal('0'))
            self.assertEqual(order._executed_value, Decimal('0'))
            self.assertEqual(order.executed_value, Decimal('0'))
            
            msg = Message(TEST_KEY, 2, 8, {39: 1, 150: 1, 31: 3000, 32: .5, 37: order.id})
            client.data_received(bytes(msg))
            
            self.assertEqual(order.status, 'partially filled')
            self.assertEqual(order.filled_size, Decimal('.5'))
            self.assertEqual(order._executed_value, Decimal('1500'))
            self.assertEqual(order.executed_value, Decimal('1500'))
            
            msg = Message(TEST_KEY, 2, 8, {39: 1, 150: 1, 31: 3001.50, 32: .25, 37: order.id})
            client.data_received(bytes(msg))
            
            self.assertEqual(order.filled_size, Decimal('.75'))
            self.assertEqual(order._executed_value, Decimal('2250.375'))
            self.assertEqual(order.executed_value, Decimal('2250.38'))
            

    async def test_data_received_exec_report_done(self):
        def receive_order(self, msg):
            assigned_id = str(uuid.uuid4())
            rec_msg = Message(TEST_KEY, 2, 8, {11: msg[11], 37: assigned_id,
                                                             39: '0', 150: '0'})
            self.data_received(bytes(rec_msg))

        with patch.object(Client, 'send', autospec=True, side_effect=receive_order):
            
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
            order = await client.market_order('buy', 'BTC-USD', 1)
            
            self.assertEqual(order.status, 'new')
            self.assertFalse(order.done.is_set())
            
            msg = Message(TEST_KEY, 1, 8, {39: 3, 150: 3, 37: order.id})
            client.data_received(bytes(msg))
            
            self.assertEqual(order.status, 'done')
            self.assertTrue(order.done.is_set())
        

    async def test_data_received_exec_report_canceled(self):
        def receive_order(self, msg):
            assigned_id = str(uuid.uuid4())
            rec_msg = Message(TEST_KEY, 2, 8, {11: msg[11], 37: assigned_id,
                                                             39: '0', 150: '0'})
            self.data_received(bytes(rec_msg))

        with patch.object(Client, 'send', autospec=True, side_effect=receive_order):
            
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
            order = await client.market_order('buy', 'BTC-USD', 1)
            
            self.assertEqual(order.status, 'new')
            self.assertFalse(order.done.is_set())
            
            msg = Message(TEST_KEY, 1, 8, {39: 4, 150: 4, 37: order.id})
            client.data_received(bytes(msg))
            
            self.assertEqual(order.status, 'canceled')
            self.assertTrue(order.done.is_set())


    async def test_data_received_multiple_messages(self):

        with patch('fix.Message.from_formatted') as patched:
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
            msg1 = Message(TEST_KEY, 1, 8, {11: 'my order id', 37: '0', 150: '0'})
            msg2 = Message(TEST_KEY, 2, 8, {11: 'my order id', 37: '3', 150: '3'})
            combo = repr(msg1) + repr(msg2)
            client.data_received(combo.encode('ascii'))
            self.assertEqual(patched.call_count, 2)
            
    def test_send(self):
        
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.transport = MagicMock()
        client.transport.write = MagicMock()
        
        msg = Message(TEST_KEY, 704, 35)
        client.send(msg)
        
        client.transport.write.assert_called_with(bytes(msg))


    async def test_connect(self):
        
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE, reconnect=False)
        client.loop.create_connection = CoroutineMock(return_value=(None, None))
        client.login = CoroutineMock()
        client.keep_alive = CoroutineMock()
        
        def test():
            self.loop.create_connection.assert_called_with(client,
                                                  'fix.pro.coinbase.com', 4198, 
                                                  ssl=client.ssl_context)
            self.assertTrue(client.connected.is_set())
            self.assertFalse(client.disconnected.is_set())
            client.login.assert_called()
            client.keep_alive.assert_called()
            self.assertFalse(client.is_closing)
            
            client.is_closing = True
            client.connection_lost()

        self.loop.call_later(1, test)

        await client.connect()


    async def test_connect_connect_attempts(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
                        url='example.com:1000', max_connect_attempts=3, connect_timeout=1)
        client.loop.create_connection = CoroutineMock(side_effect=asyncio.TimeoutError)
        client.is_closing = True
        await client.connect()
        self.assertEqual(client.loop.create_connection.call_count, 3)
        self.assertFalse(client.is_closing)
    
    
    async def test_connect_connect_timeout(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
                                 url='example.com:1000', max_connect_attempts=1)
        client.is_closing = True
        start = time.time()
        await client.connect()
        duration = time.time() - start
        self.assertGreater(duration, 9.5)
        self.assertLess(duration, 10.5)
        self.assertFalse(client.is_closing)
        
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE,
                                 url='example.com:1000', max_connect_attempts=1,
                                 connect_timeout=5)
        start = time.time()
        await client.connect()
        duration = time.time() - start
        self.assertGreater(duration, 4.5)
        self.assertLess(duration, 5.5)
    
 
    async def test_connect_reconnect(self):
        
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.loop.create_connection = CoroutineMock(return_value=(None, None))
        client.login = CoroutineMock()
        client.keep_alive = CoroutineMock()

        def test():
            self.loop.create_connection.assert_called_with(client,
                                                  'fix.pro.coinbase.com', 4198, 
                                                  ssl=client.ssl_context)
            self.assertTrue(client.connected.is_set())
            self.assertFalse(client.disconnected.is_set())
            client.login.assert_called()
            client.keep_alive.assert_called()
            self.assertFalse(client.is_closing)
            
            client.connection_lost()
            
            self.loop.call_later(1, test2)
            
        def test2():
            self.loop.create_connection.assert_called_with(client,
                                                  'fix.pro.coinbase.com', 4198, 
                                                  ssl=client.ssl_context)
            self.assertEqual(self.loop.create_connection.call_count, 2)
            self.assertTrue(client.connected.is_set())
            self.assertFalse(client.disconnected.is_set())
            client.login.assert_called()
            client.keep_alive.assert_called()
            self.assertFalse(client.is_closing)
            
            client.is_closing = True
            client.connection_lost()            
            

        self.loop.call_later(1, test)        

        await client.connect()


    async def test_close(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.transport = MagicMock()
        client.transport.close = MagicMock(side_effect=client.connection_lost)

        client.connected.set()
        client.disconnected.clear()
        client.logged_in.set()
        client.logged_out.clear()
        client.is_closing = False
        
        await client.close()
        client.transport.close.assert_called()
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
        client.is_closing = True
    
    
    async def test_login(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        resp_msg = Message(TEST_KEY, 54, 'A')
        client.send = MagicMock(side_effect=lambda x: client.data_received(bytes(resp_msg)))

        fields = {52: '1543883345.9289815', 98: 0, 108: 30, 554: TEST_PASSPHRASE, 
                  8013: 'S', 96: '6ps2fD4oRv/wwaXrP03ezMOZSmWt4FOEW1g2FoN2YNw='}
        expected = Message(TEST_KEY, 7, 'A', fields)

        client.seq_num = 6
        await client.login(send_time='1543883345.9289815')
        client.send.assert_called_with(expected)
        self.assertTrue(client.logged_in.is_set())
        self.assertFalse(client.logged_out.is_set())
        

    async def test_logout(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        resp_msg = Message(TEST_KEY, 9000, '5')
        client.send = MagicMock(side_effect=lambda x: client.data_received(bytes(resp_msg)))

        client.logged_in.set()
        client.logged_out.clear()
        client.seq_num = 8080
        
        expected = Message(TEST_KEY, 8081, '5')
        await client.logout()
        client.send.assert_called_with(expected)
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
    
    
    async def test_heartbeat(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.send = MagicMock()

        await client.heartbeat()
        client.send.assert_called_with(Message(TEST_KEY, 1, '0'))

        await client.heartbeat(333)
        
        client.send.assert_called_with(Message(TEST_KEY, 2, '0', {112: 333}))
        
        
    async def test_keep_alive(self):
        client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
        client.send = MagicMock()

        client.logged_in.set()
        client.logged_out.clear()
        
        self.loop.create_task(client.keep_alive(2))
        
        await asyncio.sleep(10)
        client.logged_out.set()
        client.logged_in.clear()
        
        self.assertGreater(client.send.call_count, 3)
        client.send.assert_any_call(Message(TEST_KEY, 1, '0'))
        

    async def test_limit_order(self):
        
        def receive_order(self, msg):
            assigned_id = str(uuid.uuid4())
            rec_msg = Message(TEST_KEY, 2, 8, {11: msg[11], 37: assigned_id,
                                                             39: '0', 150: '0'})
            self.data_received(bytes(rec_msg))
        
        with patch.object(Client, 'send', autospec=True, side_effect=receive_order):
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    
            # Invalid side
            with self.assertRaises(ValueError):
                order = await client.limit_order('right', 'BTC-USD', 100, 1)
            
            # Invalid time_in_force
            with self.assertRaises(ValueError):
                order = await client.limit_order('buy', 'BTC-USD', 5, 100, time_in_force='OPP')
    
            # Buy, default time_in_force
            order = await client.limit_order('buy', 'BTC-USD', 3.1, 1.14)
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, 'buy')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal('3.1'))
            self.assertEqual(order.price, Decimal('1.14'))
            self.assertEqual(order.time_in_force, 'GTC')
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 1)
        
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '2',
                            38: '3.1', 44: '1.14', 54: '1', 55: 'BTC-USD', 59: '1'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
       
            # Sell, PO time_in_force
            order = await client.limit_order('sell', 'LTC-USD', 5, 100, time_in_force='PO')
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, 'sell')
            self.assertEqual(order.product_id, 'LTC-USD')
            self.assertEqual(order.size, Decimal('5'))
            self.assertEqual(order.price, Decimal('100'))
            self.assertEqual(order.time_in_force, 'PO')
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 2)
    
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '2', 
                              38: '5', 44: '100', 54: '2', 55: 'LTC-USD', 59: 'P'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
        
            # Stop order with PO time_in_force
            with self.assertRaises(ValueError):
                order = await client.limit_order('sell', 'ETH-USD', 8.5, 600,
                                                 time_in_force='PO', stop_price=595)
       
            # Stop loss
            order = await client.limit_order('sell', 'BTC-USD', .001, 3.5, stop_price=4)
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'stop limit')
            self.assertEqual(order.side, 'sell')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal('.001'))
            self.assertEqual(order.price, Decimal('3.5'))
            self.assertEqual(order.time_in_force, 'GTC')
            self.assertEqual(order.stop_price, Decimal('4'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 3)
    
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '4', 
                  38: '0.001', 44: '3.5', 54: '2', 55: 'BTC-USD', 59: '1', 99: '4'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
        
            # Stop entry
            order = await client.limit_order('buy', 'BTC-USD', .005, 10000, stop_price=9900)
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'stop limit')
            self.assertEqual(order.side, 'buy')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal('.005'))
            self.assertEqual(order.price, Decimal('10000'))
            self.assertEqual(order.time_in_force, 'GTC')
            self.assertEqual(order.stop_price, Decimal('9900'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 4)
    
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '4', 
                                  38: '0.005', 44: '10000', 54: '1', 55: 'BTC-USD',
                                                              59: '1', 99: '9900'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)

    
    async def test_market_order(self):

        def receive_order(self, msg):
            assigned_id = str(uuid.uuid4())
            rec_msg = Message(TEST_KEY, 2, 8, {11: msg[11], 37: assigned_id,
                                                             39: '0', 150: '0'})
            self.data_received(bytes(rec_msg))
        
        with patch.object(Client, 'send', autospec=True, side_effect=receive_order):
       
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)
    
            # Invalid side
            with self.assertRaises(ValueError):
                order = await client.market_order('dark', 'BTC-USD', .001)
            
            # No funds or size
            with self.assertRaises(ValueError):
                order = await client.market_order('buy', 'BTC-USD')
                
            # funds and size
            with self.assertRaises(ValueError):
                order = await client.market_order('buy', 'BTC-USD', size=.001, funds=10000)
            
            # buy size
            order = await client.market_order('buy', 'BTC-USD', .001)
            
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'market')
            self.assertEqual(order.side, 'buy')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal('.001'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 1)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '1', 38: .001, 54: '1', 55: 'BTC-USD'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
        
            # buy funds
            order = await client.market_order('buy', 'LTC-USD', funds=500)
    
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'market')
            self.assertEqual(order.side, 'buy')
            self.assertEqual(order.product_id, 'LTC-USD')
            self.assertEqual(order.funds, Decimal('500'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 2)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '1', 152: 500, 54: '1', 55: 'LTC-USD'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
 
            # sell size
            order = await client.market_order('sell', 'ETH-USD', .003)
    
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'market')
            self.assertEqual(order.side, 'sell')
            self.assertEqual(order.product_id, 'ETH-USD')
            self.assertEqual(order.size, Decimal('.003'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 3)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '1', 38: .003, 54: '2', 55: 'ETH-USD'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
        
            # sell funds
            order = await client.market_order('sell', 'BTC-USD', funds=1000)
    
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'market')
            self.assertEqual(order.side, 'sell')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.funds, Decimal('1000'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 4)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '1', 152: 1000, 54: '2', 55: 'BTC-USD'})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
   
            # stop loss
            order = await client.market_order('sell', 'BTC-USD', .002, stop_price=2.2)
    
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'stop market')
            self.assertEqual(order.side, 'sell')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal('.002'))
            self.assertEqual
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 5)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '3', 38: .002, 54: '2', 55: 'BTC-USD', 99: 2.2})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
        
            # stop entry
            order = await client.market_order('buy', 'BTC-USD', .004, stop_price=9000)
    
            self.assertIsInstance(order, Order)
            self.assertIsInstance(order.client_oid, str)
            self.assertEqual(order.type, 'stop market')
            self.assertEqual(order.side, 'buy')
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal('.004'))
            self.assertEqual(order.stop_price, Decimal('9000'))
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            self.assertNotIn(order.client_oid, client.orders)
            self.assertIn(order.id, client.orders)
            self.assertEqual(len(client.orders), 6)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'D', {22: '1', 40: '3', 38: .004, 54: '1', 55: 'BTC-USD', 99: 9000})
            actual_msg = client.send.call_args[0][1]
            expected_msg[11] = actual_msg[11]
            self.assertEqual(actual_msg, expected_msg)
        
        
    async def test_cancel(self):

        def receive_order(self, msg):
            if 11 in msg:
                assigned_id = str(uuid.uuid4())
                rec_msg = Message(TEST_KEY, 2, 8, {11: msg[11], 37: assigned_id,
                                                             39: '0', 150: '0'})
                self.data_received(bytes(rec_msg))
        
        with patch.object(Client, 'send', autospec=True, side_effect=receive_order):
                  
            client = Client(self.loop, TEST_KEY, TEST_SECRET, TEST_PASSPHRASE)

            order = await client.limit_order('buy', 'BTC-USD', 3.1, 1.14)

            await client.cancel(order.id)
            
            expected_msg = Message(TEST_KEY, client.seq_num, 'F', {37: order.id})
            actual_msg = client.send.call_args[0][1]
            self.assertEqual(actual_msg, expected_msg)
