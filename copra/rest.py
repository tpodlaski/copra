# -*- coding: utf-8 -*-
"""Public (unauthenticated) and authenticated asyncronous REST client 
for the Coinbase Pro platform.

"""

import asyncio
import base64
from datetime import datetime, timedelta
import hashlib
import hmac
import sys
import time

import aiohttp
import dateutil.parser

from copra import __version__

URL = 'https://api.pro.coinbase.com'
SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com'

_user_agent = 'Python/{} copra/{}'.format(
    '.'.join([str(x) for x in sys.version_info[:3]]), __version__)

class Client():
    """Asyncronous REST client for Coinbase Pro.
    """
    
    def __init__(self, loop, url=URL, auth=False, key='', secret='', passphrase=''):
        """
        
        :param loop: The asyncio loop that the client runs in.
        :type loop: asyncio loop
        
        :param bool auth:  Whether or not the (entire) REST session is
            authenticated. If True, you will need an API key from the
            Coinbase Pro website. The default is False.
            
        :param str key:  The API key to use for authentication. Required if auth
            is True. The default is ''.
            
        :param str secret: The secret string for the API key used for
            authenticaiton. Required if auth is True. The default is ''.
            
        :param str passphrase: The passphrase for the API key used for
            authentication. Required if auth is True. The default is ''.
            
        :raises ValueError: If auth is True and key, secret, and passphrase are
            not provided.
        """
        self.loop = loop
        self.url = url
        
        if auth and not (key and secret and passphrase):
            raise ValueError('auth requires key, secret, and passphrase')
        
        self.auth = auth
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        
        self.session = aiohttp.ClientSession(loop=loop)
        
    async def close(self):
        """Close the client session and release all aquired resources.
        """
        await self.session.close()
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()
        
    def get_auth_headers(self, path, timestamp=None):
        """Get the headers necessary to authenticate a client request.
        
        :param str path: The path portion of the REST request. For example,
            '/products/BTC-USD/candles'
            
        :param float timestamp: A UNIX timestamp. This parameter exists for
            testing purposes and generally should not be used. If a timestamp
            is provided it must be within 30 seconds of the API server's time.
            This can be found using: use :meth:`rest.Client.get_server_time`.
            
        :returns: A dict of headers to be added to the request.
        
        :raises ValueError: If auth is not True.
        """
        if not self.auth:
            raise ValueError('client is not properly configured for authorization')
        
        if not timestamp:
            timestamp = time.time()
        timestamp = str(timestamp)
        message = timestamp + 'GET' + path
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    
        return {
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.key,
            'CB-ACCESS-PASSPHRASE': self.passphrase
        }
        
    async def get(self, path='/', params=None, auth=False):
        """Base method for making GET requests.
        
        :param str path: The path not including the base URL of the
            resource to be retrieved.
            
        :param dict params: Optional dictionary of key/value str pairs
            to be appended to the request. The default is None.
            
        :param boolean auth: Indicates whether or not this request needs to be
            authenticated. The default is False.
            
        :returns: A 2-tuple: (response header, response body). Headers is a dict 
            with the HTTP headers of the respone. The response body is a 
            JSON-formatted, UTF-8 encoded dict.
        """
        headers = {'USER-AGENT': _user_agent}
        
        if auth:
            headers.update(self.get_auth_headers(path))
        
        async with self.session.get(self.url + path, params=params, headers=headers) as resp:
            body = await resp.json()
            headers = dict(resp.headers)
            return (headers, body)
            
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
        headers, body = await self.get('/products')
        return body
        
    async def get_order_book(self, product_id, level=1):
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
            
        headers, body = await self.get('/products/{}/book'.format(product_id), 
                                       params={'level': level})
        return body
        
    async def get_ticker(self, product_id):
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
        
        .. note:: Polling is discouraged in favor of connecting via the 
            websocket stream and listening for match messages.
        
        """
        header, body = await self.get('/products/{}/ticker'.format(product_id))
        return body
        
    async def get_trades(self, product_id, limit=100, before=None, after=None):
        """List the latest trades for a product.
        
        The trade side indicates the maker order side. The maker order is the 
        order that was open on the order book. buy side indicates a down-tick 
        because the maker was a buy order and their order was removed. 
        Conversely, sell side indicates an up-tick.
        
        .. note:: This method is paginated. Methods that can return multiple 
           pages of results return a 3-tuple instead of a just  dict or list like 
           other methods. The first item in the tuple is the page of results -
           a list or dict similar to other methods. The 2nd and 3rd items are
           cursors for making requests for newer/earlier pages, the before cursor 
           which the second item, and for making requests for older/later pages,
           the after cursor which is the 3rd item.
        
        :param str product_id: The product id whose trades are to be retrieved.
            The product id is a string consisting of a base currency and a 
            quote currency. eg., BTC-USD, ETH-EUR, etc. To see all of the 
            product ids, use :meth:`rest.Client.get_products`.
            
        :param int limit: The number of trades to be returned per request. The
            default (and maximum) value is 100.
            
        :param int before: The before cursor value. Used to reuest a page of
            results newer than a previous request. This would be the before 
            cursor returned in that earlier call to this method.
        
        :param int after: The after cursor value. Used to reuest a page of
            results older than a previous request. This would be the older 
            cursor returned in that earlier call to this method.
            
        :returns: A 3-tuple: (trades, before cursor, after cursor)
            The first item is a list of dicts representing trades for the 
            product specified. The second item is the before cursor which
            can be used in squbsequent calls to retrieve a page of results
            newer than this one. The third item is the after cursor which 
            can be used in subsequent calls to retrieve the page of results 
            that is older than this one. NOTE: the before cursor and after
            cursor may be None if there is not an earlier page or later page
            respectively.
        
        :Example:
        
        (
          [
            {
              'time': '2018-09-27T22:49:16.105Z', 
              'trade_id': 51584925, 
              'price': '6681.01000000', 
              'size': '0.02350019', 
              'side': 'sell'
            }, 
            {
              'time': '2018-09-27T22:49:12.39Z', 
              'trade_id': 51584924, 
              'price': '6681.00000000', 
              'size': '0.01020000', 
              'side': 'buy'
            },
            ...
          ],
          '51590012', 
          '51590010'
        )
        """
        params = {'limit': limit}
        if before:
            params.update({'before': before})
        if after:
            params.update({'after': after})
            
        headers, body = await self.get('/products/{}/trades'.format(product_id),
                                       params)
        return (body, headers.get('cb-before', None), headers.get('cb-after', None))
        
    async def get_historic_rates(self, product_id, granularity=3600, start=None, stop=None):
        """Historic rates for a product. 
        
        Rates are returned in grouped buckets based on requested granularity.
        
        ..note:: The maximum number of data points for a single request is 300 
            candles. If your selection of start/end time and granularity will 
            result in more than 300 data points, your request will be rejected. 
            If you wish to retrieve fine granularity data over a larger time 
            range, you will need to make multiple requests with new start/end 
            ranges.
          
        ..note::  Historical rate data may be incomplete. No data is published 
            for intervals where there are no ticks.
        
        :param str product_id: The product id whose rates are to be retrieved.
            The product id is a string consisting of a base currency and a 
            quote currency. eg., BTC-USD, ETH-EUR, etc. To see all of the 
            product ids, use :meth:`rest.Client.get_products`.
        
        :param int granularity: Desired timeslice in seconds. The granularity 
            field must be one of the following values: {60, 300, 900, 3600, 
            21600, 86400}. Otherwise, your request will be rejected. These 
            values correspond to timeslices representing one minute, five 
            minutes, fifteen minutes, one hour, six hours, and one day, 
            respectively. The default is 3600 (1 hour).
            
        :param str start: The start time of the requested historic rates as 
            a str in ISO 8601 format. This field is optional. If it is set, 
            then stop must be set as well If neither start nor stop are set, 
            start will default to the time relative to now() that would return 
            300 results based on the granularity.
        
        :param datetime stop: The end time of the requested historic rates as a
            str in ISO 8601 format. This field is optional. If it is set then 
            start must be set as well. If it is not set, stop will default to 
            now().
        
         .. note:: If either one of the start or end fields are not provided 
            then both fields will be ignored. If a custom time range is not 
            declared then one ending now is selected.
            
        :returns: A list of lists where each list item is a "bucket" 
            representing a timeslice of length granularity. The fields of the
            bucket are: [ time, low, high, open, close, volume ]
            
            * **time** bucket start time as a Unix timestamp
            * **low** lowest price during the bucket interval
            * **high** highest price during the bucket interval
            * **open** opening price (first trade) in the bucket interval
            * **close** closing price (last trade) in the bucket interval
            * **volume** volume of trading activity during the bucket interval
            
        :Example:
        
        [
          [1538179200, 61.12, 61.75, 61.74, 61.18, 2290.8172972700004], 
          [1538175600, 61.62, 61.8, 61.65, 61.75, 2282.2335001199995], 
          [1538172000, 61.52, 61.79, 61.66, 61.65, 3877.4680861400007],
          ...
        ]
            
        :raises ValueError: If granularity is not one of the possible values.
        
        .. warning:: Historical rates should not be polled frequently. If you 
            need real-time information, use the trade and book endpoints along 
            with the websocket feed.
        """
        if granularity not in (60, 300, 900, 3600, 21600, 86400):
            raise ValueError("invalid granularity {}".format(granularity))
            
        params = {'granularity': granularity}
        
        if start and stop:
            params.update({'start': start, 'stop': stop})
            
        headers, body = await self.get('/products/{}/candles'.format(product_id),
                                       params=params)
                                       
        if start and stop:
            return [x for x in body if x[0] >= dateutil.parser.parse(start).timestamp()]
        return body
        
    async def get_24hour_stats(self, product_id):
        """Get 24 hr stats for a product.
        
        :param str product_id: The product id whose stats are to be retrieved.
            The product id is a string consisting of a base currency and a 
            quote currency. eg., BTC-USD, ETH-EUR, etc. To see all of the 
            product ids, use :meth:`rest.Client.get_products`.
            
        :returns: A dict of stats for the product including: open, high, low,
            volume, last price, and 30 day volume.
            
        :Example:
        
        {
          'open': '6710.37000000', 
          'high': '6786.73000000', 
          'low': '6452.02000000', 
          'volume': '9627.98224214', 
          'last': '6484.03000000', 
          'volume_30day': '238376.24964395'
        }
        """
        headers, body = await self.get('/products/{}/stats'.format(product_id))
        return body
        
    async def get_currencies(self):
        """List known currencies.
        
        Currency codes will conform to the ISO 4217 standard where possible. 
        Currencies which have or had no representation in ISO 4217 may use a 
        custom code.
        
        ..note:: Not all currencies may be currently in use for trading.
        
        :returns: A list of dicts where each dict contains information about a
            currency.
            
        :Example:
        
        [
          {
            'id': 'BTC', 
            'name': 'Bitcoin', 
            'min_size': '0.00000001', 
            'status': 'online', 
            'message': None
          },
          ...
        ]
        
        """
        headers, body = await self.get('/currencies')
        return body
        
    async def get_server_time(self):
        """Get the API server time.
        
        :returns: A dict with two fields: iso and epoch. iso is an ISO 8601 str,
            and epoch is a float. Both represent the current time at the API
            server.
            
        :Example:
        
        {
          'iso': '2018-09-29T03:02:27.753Z', 
          'epoch': 1538190147.753
        }
        """
        headers, body = await self.get('/time')
        return body
        
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    
    client = Client(loop)
    
    results = None
    
    async def go():
        global results
        results = await client.get_server_time()

    loop.run_until_complete(go())
    loop.run_until_complete(client.close())
    
    loop.close()
        
        
    