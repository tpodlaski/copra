#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Order` class.
"""

from asynctest import TestCase

from copra.order import Order

class TestOrder(TestCase):
    
    def test___init__(self):
        order = Order()
        self.assertIsInstance(order.client_oid, str)