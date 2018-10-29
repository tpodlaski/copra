#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `copra.rest.BaseClient` class.
"""

import asyncio

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
        

    async def test_delete(self):
        
        #url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.delete()

        url = 'http://httpbin.org/'
        params = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        #No params, default headers
        resp = await self.client.delete(url)
        self.check_mock_req_args(self.mock_del, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_del, url, {})
        self.check_mock_req_headers(self.mock_del, HEADERS)
        
        #Params, default headers
        resp = await self.client.delete(url, params=params)
        self.check_mock_req_args(self.mock_del, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_del, url, params)
        self.check_mock_req_headers(self.mock_del, HEADERS)

        #Params, no headers
        resp = await self.client.delete(url, params=params, headers={})
        self.check_mock_req_args(self.mock_del, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_del, url, params)
        self.check_mock_req_headers(self.mock_del, {})
        
        #Params, custom headers
        resp = await self.client.delete(url, params=params, headers=headers)
        self.check_mock_req_args(self.mock_del, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_del, url, params)
        self.check_mock_req_headers(self.mock_del, headers)


    async def test_get(self):
        
        #url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.get()
        
        url = 'http://httpbin.org/'
        params = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        #No params, default headers
        resp = await self.client.get(url)
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, {})
        self.check_mock_req_headers(self.mock_get, HEADERS)
        
        #Params, default headers
        resp = await self.client.get(url, params)
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, params)
        self.check_mock_req_headers(self.mock_get, HEADERS)
        
        #Params, no headers
        resp = await self.client.get(url, params, headers={})
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, params)
        self.check_mock_req_headers(self.mock_get, {})
        
        #Params, custom headers
        resp = await self.client.get(url, params, headers=headers)
        self.check_mock_req_args(self.mock_get, [str], {'headers': dict})
        self.check_mock_req_url(self.mock_get, url, params)
        self.check_mock_req_headers(self.mock_get, headers)
        
        
        
    async def test_post(self):
        
        #url is required
        with self.assertRaises(TypeError):
            async with BaseClient(self.loop) as client:
                resp = client.post()
                
        url = 'http://httpbin.org'
        data = {'key1': 'item1', 'key2': 'item2'}
        headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        #No data, default headers
        resp = await self.client.post(url)
        self.check_mock_req_args(self.mock_post, [str], {'data': dict, 
                                                         'headers': dict})
        self.check_mock_req_url(self.mock_post, url, {})
        self.check_mock_req_headers(self.mock_post, HEADERS)
        self.check_mock_req_data(self.mock_post, {})
                                                         
        #Data, default headers
        resp = await self.client.post(url, data)
        self.check_mock_req_args(self.mock_post, [str], {'data': dict, 
                                                         'headers': dict})
        self.check_mock_req_url(self.mock_post, url, {})
        self.check_mock_req_headers(self.mock_post, HEADERS)
        self.check_mock_req_data(self.mock_post, data)
        
        #Data, no headers
        resp = await self.client.post(url, data, headers={})
        self.check_mock_req_args(self.mock_post, [str], {'data': dict, 
                                                         'headers': dict})
        self.check_mock_req_url(self.mock_post, url, {})
        self.check_mock_req_headers(self.mock_post,{})
        self.check_mock_req_data(self.mock_post, data)
        
        #Data, custom headers
        resp = await self.client.post(url, data, headers=headers)
        self.check_mock_req_args(self.mock_post, [str], {'data': dict, 
                                                         'headers': dict})
        self.check_mock_req_url(self.mock_post, url, {})
        self.check_mock_req_headers(self.mock_post,headers)
        self.check_mock_req_data(self.mock_post, data)