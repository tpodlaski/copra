#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.BaseClient` class.
"""

import asyncio
import json

import aiohttp

from copra.rest import BaseClient, HEADERS
from tests.unit.rest.util import MockTestCase

        
class TestBaseClient(MockTestCase):
    """Tests for copra.rest.BaseClient"""
    
    def setUp(self):
        super().setUp()
        self.client = BaseClient(self.loop)
        
    def tearDown(self):
        self.loop.create_task(self.client.close())
        self.loop.run_until_complete(asyncio.sleep(0.250))

    
    async def test___init__(self):
        self.assertEqual(self.client.loop, self.loop)
        self.assertIsInstance(self.client.session, aiohttp.ClientSession)
        self.assertFalse(self.client.session.closed)


    async def test_close(self):
        self.assertFalse(self.client.session.closed)
        self.assertFalse(self.client.closed)
        await self.client.close()
        self.assertTrue(self.client.session.closed)
        self.assertTrue(self.client.closed)

        
    async def test_context_manager(self):
        async with BaseClient(self.loop) as client:
            self.assertFalse(client.closed)
        self.assertTrue(client.closed)
    
        try:
            async with BaseClient(self.loop) as client:
                raise ValueError()
        except ValueError:
            pass
        self.assertTrue(client.closed)
        

    async def test__request(self):
        # invalid method
        with self.assertRaises(ValueError):
            resp = await self.client._request('punch', 'http://www.example.com')


    async def test_delete(self):
        
        # url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.delete()

        url = 'http://httpbin.org/'
        params = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        # No params, default headers
        resp = await self.client.delete(url)
        self.check_req(self.mock_del, url, query={}, headers=HEADERS)

        # Params, default headers
        resp = await self.client.delete(url, params=params)
        self.check_req(self.mock_del, url, query=params, headers=HEADERS)

        # Params, no headers
        resp = await self.client.delete(url, params=params, headers={})
        self.check_req(self.mock_del, url, query=params, headers={})
        
        # Params, custom headers
        resp = await self.client.delete(url, params=params, headers=headers)
        self.check_req(self.mock_del, url, query=params, headers=headers)


    async def test_get(self):
        
        # url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.get()
        
        url = 'http://httpbin.org/'
        params = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        # No params, default headers
        resp = await self.client.get(url)
        self.check_req(self.mock_get, url, query={}, headers=HEADERS)

        # Params, default headers
        resp = await self.client.get(url, params)
        self.check_req(self.mock_get, url, query=params, headers=HEADERS)
        
        # Params, no headers
        resp = await self.client.get(url, params, headers={})
        self.check_req(self.mock_get, url, query=params, headers={})
        
        # Params, custom headers
        resp = await self.client.get(url, params, headers=headers)
        self.check_req(self.mock_get, url, query=params, headers=headers)


    async def test_post(self):
        
        # url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.post()
                
        url = 'http://httpbin.org'
        data = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        # No data, default headers
        resp = await self.client.post(url)
        self.check_req(self.mock_post, url, data={}, headers=HEADERS)
                                                         
        # Data, default headers
        resp = await self.client.post(url, data)
        self.check_req(self.mock_post, url, data=data, headers=HEADERS)
        
        # Data, no headers
        resp = await self.client.post(url, data, headers={})
        self.check_req(self.mock_post, url, data=data, headers={})
        
        # Data, custom headers
        resp = await self.client.post(url, data, headers=headers)
        self.check_req(self.mock_post, url, data=data, headers=headers)
