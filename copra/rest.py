# -*- coding: utf-8 -*-
"""Public (unauthenticated) and authenticated asyncronous REST client 
for the Coinbase Pro platform.

"""

import asyncio
import logging
import sys

import aiohttp

from copra import __version__

logger = logging.getLogger(__name__)

URL = 'https://api.pro.coinbase.com'
SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com'

_user_agent = 'Python/{} copra/{}'.format(
    '.'.join([str(x) for x in sys.version_info[:3]]), __version__)

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
        
    async def get(self, path='/', params=None, raw=False):
        """Base method for making GET requests.
        
        :param str path: The path not including the base URL of the
            resource to be retrieved.
            
        :param dict params: Optional dictionary of key/value str pairs
            to be appended to the request. The default is None.
            
        :param bool raw: Return the raw aiohttp.ClientResponse. This is useful
            for debugging. The default is False.
            
        :returns: The response body as JSON-formatted, UTF-8 encoded dict or
            aiohttp.ClientResponse if raw is True.
        """
        
        headers = {'USER-AGENT': _user_agent}
        
        async with self.session.get(self.url + path, params=params, headers=headers) as resp:
            if raw:
                return resp
            return await resp.json()
            
    
    