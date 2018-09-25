# -*- coding: utf-8 -*-
"""Public (unauthenticated) and authenticated asyncronous REST client 
for the Coinbase Pro platform.

"""

import asyncio
import logging

import aiohttp

logger = logging.getLogger(__name__)

URL = 'https://api.pro.coinbase.com'
SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com'

class Client():
    """Asyncronous REST client for Coinbase Pro.
    """
    
    def __init__(self, loop, url=URL):
        """
        
        :param loop: The asyncio loop that the client runs in.
        :type loop: asyncio loop
        """
        self.loop = loop
        self.url = url
        self.session = aiohttp.ClientSession(loop=loop)
        
    async def close(self):
        """Close the client session and release all aquired resources.
        """
        await self.session.close()
        
    