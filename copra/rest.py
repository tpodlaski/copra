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
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
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
        
    async def get_product_order_book(self, product_id, level=1):
        """Get a list of open orders for a product. 
        
        By default, only the inside (i.e. best) bid and ask are returned. This 
        is equivalent to a book depth of 1 level. If you would like to see a 
        larger order book, specify the level query parameter.

        :param str product_id: The product id whose order book you wish to 
            view. The product id is a string consisting of a base currency
            and a quote currency. eg., BTC-USD, ETH-EUR, etc. To see all of 
            the product ids, use :meth:`rest.Client.get_products`.
            
        :param int level: The level customizes the amount of detail shown. See
            below for more detail. The default is 1.
            
         **Levels**
        
        +--------------------------------------------------------------------+
        | Level | Description                                                |
        +=======+============================================================+
        |   1   | Only the best bid and ask                                  |
        +-------+------------------------------------------------------------+
        |   2   | Top 50 bids and asks (aggregated)                          |
        +-------+------------------------------------------------------------+
        |   3   | Full order book (non aggregated)                           |
        +-------+------------------------------------------------------------+
        
        If a level is not aggregated, then all of the orders at each price 
        will be returned. Aggregated levels return only one size for each 
        active price (as if there was only a single order for that size at 
        the level).
        
        Levels 1 and 2 are aggregated. The first field is the price. The second
        is the size which is the sum of the size of the orders at that price, 
        and the third is the number of orders, the count of orders at 
        that price. The size should not be multiplied by the number of orders.

        Level 3 is non-aggregated and returns the entire order book.
        
        .. note:: This request is NOT paginated. The entire book is returned in 
            one response.
            
        .. note:: Level 1 and Level 2 are recommended for polling. For the most 
            up-to-date data, consider using the websocket stream.
            
        .. warning:: Level 3 is only recommended for users wishing to maintain 
            a full real-time order book using the websocket stream. Abuse of 
            Level 3 via polling will cause your access to be limited or 
            blocked.
            
        :returns: A dict representing the order book for the product id
            specified. The layout of the dict will vary based on the level. See
            the examples below.
            
        :Example:
        
        **Level 1**
        
        {
          'sequence': 7068939079, 
          'bids': [['6482.98', '54.49144003', 18]], 
          'asks': [['6482.99', '4.57036219', 10]]
        }
        
        **Level 2**
        
        {
          'sequence': 7069016926, 
          'bids': [['6489.13', '0.001', 1], ['6487.99', '0.03', 1], ...],
          'asks': [['6489.14', '40.72125158', 16], ['6490.11', '0.5', 1], ...],
        }
        
        **Level 3**
        
        {
          'sequence': 7072737439, 
          'bids': [
                    ['6468.9', '0.01100413', '48c3ed25-616d-430d-bab4-cb338b489a33'], 
                    ['6468.9', '0.224', 'b96424ea-e992-4df5-b503-df50dac1ac50'], 
                    ...
                  ],
          'asks': [
                    ['6468.91', '5.96606527', 'cc37e457-020c-4843-9a3e-e6164dcf4e60'], 
                    ['6468.91', '0.00341509', '43e8158a-30c6-437b-9a51-9b9da00e4e22'],
                    ...
                  ]
        }
           
        :raises ValueError: If level not 1, 2, or 3.
        """
        
        if level not in (1, 2, 3):
            raise ValueError("level must be 1, 2, or 3")    
            
        resp = await self.get('/products/{}/book'.format(product_id), 
                              params={'level': level})
        return resp
        
    async def get_product_ticker(self, product_id):
        """Get information about the last trade for a specific product.
        
        :param str product_id: The product id of the tick to be retrieved.
            The product id is a string consisting of a base currency and a 
            quote currency. eg., BTC-USD, ETH-EUR, etc. To see all of the 
            product ids, use :meth:`rest.Client.get_products`.
            
        :returns: A dict containing information about the last trade (tick) for
           the product.
           
        :Example:
        
        {
          'trade_id': 51554088, 
          'price': '6503.14000000', 
          'size': '0.00532605', 
          'bid': '6503.13', 
          'ask': '6503.14', 
          'volume': '6060.89272148', 
          'time': '2018-09-27T13:18:42.571000Z'
        }
        
        """
        resp = await self.get('/products/{}/ticker'.format(product_id))
        return resp
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    
    client = Client(loop)
    
    async def go():
        tick = await client.get_product_ticker('BTC-USD')
        print(tick)
        
    
    loop.run_until_complete(go())
    loop.run_until_complete(client.close())
    
    loop.close()
        
        
    