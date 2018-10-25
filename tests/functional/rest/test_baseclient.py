#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.rest.BaseClient` class.
"""

import asyncio

from asynctest import TestCase

from copra.rest import BaseClient, USER_AGENT

HTTPBIN = 'http://httpbin.org'

class TestBaseClient(TestCase):
    """Tests for copra.rest.BaseClient"""
    
    def setUp(self):
        self.client = BaseClient(self.loop)
        
    def tearDown(self):
        self.loop.create_task(self.client.close())
        self.loop.run_until_complete(asyncio.sleep(0.250))

    async def test_user_agent(self):
        
        # Default agent
        resp = await self.client.get(HTTPBIN + '/user-agent')
        ua_dict = await resp.json()
        self.assertEqual(ua_dict['user-agent'], USER_AGENT)
        
        # Custom agent
        resp = await self.client.get(HTTPBIN + '/user-agent',
                                     headers={'USER-AGENT': 'Maxwell Smart'})
        ua_dict = await resp.json()
        self.assertEqual(ua_dict['user-agent'], 'Maxwell Smart')
        
    async def test_headers(self):
        
        req_headers = {'USER-AGENT': '007', 'Content-Type': 'shaken'}
        
        resp = await self.client.get(HTTPBIN + '/headers', headers=req_headers)
        headers = await resp.json()
        self.assertEqual(headers['headers']['User-Agent'], '007')
        self.assertEqual(headers['headers']['Content-Type'], 'shaken')
        
    async def test_get(self):
        
        resp = await self.client.get(HTTPBIN + '/get')
        args = (await resp.json())['args']
        self.assertEqual(args, {})
                                     
        params = {'key1': 'item1', 'key2': 'item2'}
        resp = await self.client.get(HTTPBIN + '/get',
                                     params=params)
        args = (await resp.json())['args']
        self.assertEqual(args, params)