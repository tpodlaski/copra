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
            
    async def get_products(self):
        """Get a list of available currency pairs for trading.
        
        Returns a list of dicts where each dict represents a currency pair. 
        
        The base_min_size and base_max_size fields define the min and max order 
        size. The quote_increment field specifies the min order price as well 
        as the price increment. The order price must be a multiple of this 
        increment (i.e. if the increment is 0.01, order prices of 0.001 or 
        0.021 would be rejected).
        
        :returns: A list of dicts representing the currency pairs available
            for trading.
            
        :Example:
        
        [
          {
            'id': 'BTC-USD', 
            'base_currency': 'BTC', 
            'quote_currency': 'USD', 
            'base_min_size': '0.001', 
            'base_max_size': '70', 
            'quote_increment': '0.01', 
            'display_name': 'BTC/USD', 
            'status': 'online', 
            'margin_enabled': False, 
            'status_message': None, 
            'min_market_funds': '10', 
            'max_market_funds': '1000000', 
            'post_only': False, 
            'limit_only': False, 
            'cancel_only': False
          },
          ...
         ]
            
        .. note:: Product ID will not change once assigned to a product but 
            the min/max/quote sizes can be updated in the future.
        """
        resp = await self.get('/products')
        return resp
        

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    
    client = Client(loop)
    
    async def go():
        products = await client.get_products()
        print(products)
        
    
    loop.run_until_complete(go())
    loop.run_until_complete(client.close())
    
    loop.close()
        
        
    