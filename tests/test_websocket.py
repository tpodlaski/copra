#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cbprotk.websocket` module."""


import unittest

from cbprotk.websocket import Channel


class TestChannel(unittest.TestCase):
    """Tests for cbprotk.websocket.Channel"""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test__init__(self):
        #no channel name
        with self.assertRaises(TypeError):
            channel = Channel()
            
        #valid name
        channel = Channel('heartbeat')
        self.assertEqual(channel.name, 'heartbeat')

        #invalid name
        with self.assertRaises(ValueError):
            channel = Channel('pulse')
            
        #lower case
        channel = Channel('TiCKeR')
        self.assertEqual(channel.name, 'ticker')