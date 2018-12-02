#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.fix.Client` class.
"""

import asyncio
import os

from asynctest import TestCase

from copra.fix import Client, URL, SANDBOX_URL, CERT_FILE, SANDBOX_CERT_FILE

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
        