#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Order` class.
"""

from decimal import Decimal
import uuid

from asynctest import TestCase

from copra.message import Message
from copra.order import Order


# These are made up
TEST_KEY = 'a035b37f42394a6d343231f7f772b99d'
TEST_SECRET = 'aVGe54dHHYUSudB3sJdcQx4BfQ6K5oVdcYv4eRtDN6fBHEQf5Go6BACew4G0iFjfLKJHmWY5ZEwlqxdslop4CC=='
TEST_PASSPHRASE = 'a2f9ee4dx2b'


class TestOrder(TestCase):
    
    def test__create(self):

        # Invalid side
        with self.assertRaises(ValueError):
            Order._create(TEST_KEY, 1, 'dark', 'BTC-USD')        
        
        (order, msg) = Order._create(TEST_KEY, 1, 'buy', 'BTC-USD')
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertIsNone(order.id)
        self.assertIsNone(order.status)
        self.assertEqual(order.filled_size, Decimal('0'))
        self.assertEqual(order._executed_value, Decimal('0'))
        self.assertEqual(order.executed_value, Decimal('0'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
    
        expected_msg = Message(TEST_KEY, 1, 'D', {22: '1', 54: '1', 55: 'BTC-USD'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)

    def test_executed_value(self):
        order, _ = Order._create(TEST_KEY, 1, 'buy', 'BTC-USD')
        self.assertEqual(order._executed_value, Decimal('0'))
        self.assertEqual(order.executed_value, Decimal('0'))
        
        order._executed_value = Decimal('75.36')
        self.assertEqual(order.executed_value, Decimal('75.36'))
        
        order._executed_value = Decimal('1000')
        self.assertEqual(order.executed_value, Decimal('1000'))
        
        order._executed_value = Decimal('999.9')
        self.assertEqual(order.executed_value, Decimal('999.9'))
        
        order._executed_value = Decimal('1.234')
        self.assertEqual(order.executed_value, Decimal('1.24'))
        
        order._executed_value = Decimal('123.456')
        self.assertEqual(order.executed_value, Decimal('123.46'))
        

    def test_limit_order(self):
        
        # Invalid side
        with self.assertRaises(ValueError):
            Order.market_order(TEST_KEY, 1, 'dark', 'BTC-USD', .001)

        # Invalid time_in_force
        with self.assertRaises(ValueError):
            Order.limit_order(TEST_KEY, 2, 'buy', 'BTC-USD', 100, 5, time_in_force='OPP')
            
        # Buy, default time_in_force
        (order, msg) = Order.limit_order(TEST_KEY, 3, 'buy', 'BTC-USD', 3.1, 1.14)
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'limit')
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('3.1'))
        self.assertEqual(order.price, Decimal('1.14'))
        self.assertEqual(order.time_in_force, 'GTC')
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())

        expected_msg = Message(TEST_KEY, 3, 'D', {22: '1', 40: '2', 38: '3.1', 44: '1.14', 54: '1', 55: 'BTC-USD', 59: '1'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
        # Sell, PO time_in_force
        (order, msg) = Order.limit_order(TEST_KEY, 4, 'sell', 'LTC-USD', 5, 100, time_in_force='PO')
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'limit')
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.product_id, 'LTC-USD')
        self.assertEqual(order.size, Decimal('5'))
        self.assertEqual(order.price, Decimal('100'))
        self.assertEqual(order.time_in_force, 'PO')
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())

        expected_msg = Message(TEST_KEY, 4, 'D', {22: '1', 40: '2', 38: '5', 44: '100', 54: '2', 55: 'LTC-USD', 59: 'P'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
        # Stop order with PO time_in_force
        with self.assertRaises(ValueError):
            (order, msg) = Order.limit_order(TEST_KEY, 5, 'sell', 'ETH-USD', 8.5,
                                         600, time_in_force='PO', stop_price=595)


        # Stop loss
        (order, msg) = Order.limit_order(TEST_KEY, 6, 'sell', 'BTC-USD', .001,
                                                              3.5, stop_price=4)
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'stop limit')
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.001'))
        self.assertEqual(order.price, Decimal('3.5'))
        self.assertEqual(order.time_in_force, 'GTC')
        self.assertEqual(order.stop_price, Decimal('4'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())

        expected_msg = Message(TEST_KEY, 6, 'D', {22: '1', 40: '4', 38: '0.001', 
                           44: '3.5', 54: '2', 55: 'BTC-USD', 59: '1', 99: '4'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
        # Stop entry
        (order, msg) = Order.limit_order(TEST_KEY, 7, 'buy', 'BTC-USD', .005, 
                                                         10000, stop_price=9900)
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'stop limit')
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.005'))
        self.assertEqual(order.price, Decimal('10000'))
        self.assertEqual(order.time_in_force, 'GTC')
        self.assertEqual(order.stop_price, Decimal('9900'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())

        expected_msg = Message(TEST_KEY, 7, 'D', {22: '1', 40: '4', 38: '0.005', 
                      44: '10000', 54: '1', 55: 'BTC-USD', 59: '1', 99: '9900'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
    def test_market_order(self):
        
        # Invalid side
        with self.assertRaises(ValueError):
            Order.market_order(TEST_KEY, 1, 'dark', 'BTC-USD', .001)
        
        # No funds or size
        with self.assertRaises(ValueError):
            Order.market_order(TEST_KEY, 2, 'buy', 'BTC-USD')
            
        # funds and size
        with self.assertRaises(ValueError):
            Order.market_order(TEST_KEY, 3, 'buy', 'BTC-USD', size=.001, funds=10000)
            
        # buy size
        (order, msg) = Order.market_order(TEST_KEY, 5, 'buy', 'BTC-USD', .001)
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'market')
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.001'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        expected_msg = Message(TEST_KEY, 5, 'D', {22: '1', 40: '1', 38: .001, 54: '1', 55: 'BTC-USD'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
        # buy funds
        (order, msg) = Order.market_order(TEST_KEY, 6, 'buy', 'LTC-USD', funds=500)
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'market')
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'LTC-USD')
        self.assertEqual(order.funds, Decimal('500'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        expected_msg = Message(TEST_KEY, 6, 'D', {22: '1', 40: '1', 152: 500, 54: '1', 55: 'LTC-USD'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
        # sell size
        (order, msg) = Order.market_order(TEST_KEY, 7, 'sell', 'ETH-USD', .003)
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'market')
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.product_id, 'ETH-USD')
        self.assertEqual(order.size, Decimal('.003'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        expected_msg = Message(TEST_KEY, 7, 'D', {22: '1', 40: '1', 38: .003, 54: '2', 55: 'ETH-USD'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)

        # sell funds
        (order, msg) = Order.market_order(TEST_KEY, 8, 'sell', 'BTC-USD', funds=1000)
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'market')
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.funds, Decimal('1000'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        expected_msg = Message(TEST_KEY, 8, 'D', {22: '1', 40: '1', 152: 1000, 54: '2', 55: 'BTC-USD'})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
        # stop loss
        (order, msg) = Order.market_order(TEST_KEY, 9, 'sell', 'BTC-USD', .002, stop_price=2.2)
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'stop market')
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.002'))
        self.assertEqual(order.stop_price, Decimal('2.2'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        expected_msg = Message(TEST_KEY, 9, 'D', {22: '1', 40: '3', 38: .002, 54: '2', 55: 'BTC-USD', 99: 2.2})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)

        # stop entry
        (order, msg) = Order.market_order(TEST_KEY, 10, 'buy', 'BTC-USD', .004, stop_price=9000)
        
        self.assertIsInstance(order, Order)
        self.assertIsInstance(order.client_oid, str)
        self.assertEqual(order.type, 'stop market')
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.004'))
        self.assertEqual(order.stop_price, Decimal('9000'))
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        expected_msg = Message(TEST_KEY, 10, 'D', {22: '1', 40: '3', 38: .004, 54: '1', 55: 'BTC-USD', 99: 9000})
        expected_msg[11] = msg[11]
        self.assertEqual(msg, expected_msg)
        
    
    def test_fix_update_new(self):
        order, _ = Order.market_order(TEST_KEY, 1, 'buy', 'BTC-USD', .001)
        self.assertIsNone(order.id)
        self.assertIsNone(order.status)
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())

        assigned_id = str(uuid.uuid4())
        msg = Message(TEST_KEY, 2, 8, {37: assigned_id, 39: '0', 150: '0'})
        order.fix_update(msg)
        
        self.assertEqual(order.id, assigned_id)
        self.assertEqual(order.status, 'new')
        self.assertTrue(order.received.is_set())
        self.assertFalse(order.done.is_set())
        
        
    def test_fix_update_rejected(self):
        order, _ = Order.market_order(TEST_KEY, 1, 'buy', 'BTC-USD', .001)
        self.assertIsNone(order.id)
        self.assertIsNone(order.status)
        self.assertFalse(order.received.is_set())
        self.assertFalse(order.done.is_set())

        assigned_id = str(uuid.uuid4())
        msg = Message(TEST_KEY, 2, 8, {37: assigned_id, 39: '8', 150: '8', 58: 'TOO LATE'})
        order.fix_update(msg)
        
        self.assertEqual(order.id, assigned_id)
        self.assertEqual(order.status, 'rejected')
        self.assertEqual(order.reject_reason, 'TOO LATE')
        self.assertTrue(order.received.is_set())
        self.assertTrue(order.done.is_set())
        
        
    def test_fix_update_fill(self):
        order, _ = Order.market_order(TEST_KEY, 1, 'buy', 'BTC-USD', 1)
        
        msg = Message(TEST_KEY, 1, 8, {39: 1, 150: 1, 31: 3000, 32: .5})
        order.fix_update(msg)
        
        self.assertEqual(order.status, 'partially filled')
        self.assertEqual(order.filled_size, Decimal('.5'))
        self.assertEqual(order._executed_value, Decimal('1500'))
        self.assertEqual(order.executed_value, Decimal('1500'))
        
        msg = Message(TEST_KEY, 2, 8, {39: 1, 150: 1, 31: 3001.50, 32: .25})
        order.fix_update(msg)
        
        self.assertEqual(order.status, 'partially filled')
        self.assertEqual(order.filled_size, Decimal('.75'))
        self.assertEqual(order._executed_value, Decimal('2250.375'))
        self.assertEqual(order.executed_value, Decimal('2250.38'))
        