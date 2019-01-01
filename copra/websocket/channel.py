# -*- coding: utf-8 -*-
"""WebSocket channel class for use with the copra WebSocket client.

"""

class Channel:
    """A WebSocket channel.

    A Channel object encapsulates the Coinbase Pro WebSocket channel name
    *and* one or more Coinbase Pro product ids.

    To read about Coinbase Pro channels and the data they return, visit:
    https://docs.gdax.com/#channels
    
    :ivar str name: The name of the WebSocket channel.
    :ivar product_ids: Product ids for the channel.
    :vartype product_ids: set of str
    """

    def __init__(self, name, product_ids):
        """
        
        :param str name: The name of the WebSocket channel. Possible values are 
            heatbeat, ticker, level2, full, matches, or user

        :param product_ids: A single product id (eg., 'BTC-USD') or list of 
            product ids (eg., ['BTC-USD', 'ETH-EUR', 'LTC-BTC'])
        :type product_ids: str or list of str
        
        :raises ValueError: If name not valid or product ids is empty.
        """
        self.name = name.lower()
        if self.name not in ('heartbeat', 'ticker', 'level2',
                             'full', 'matches', 'user'):
            raise ValueError("invalid name {}".format(name))

        if not product_ids:
            raise ValueError("must include at least one product id")

        if not isinstance(product_ids, list):
            product_ids = [product_ids]
        self.product_ids = set(product_ids)

    def __repr__(self):
        return str(self._as_dict())

    def _as_dict(self):
        """Returns the Channel as a dictionary.
        
        :returns dict: The Channel as a dict with keys name & value list
            of product_ids.
        """
        return {'name': self.name, 'product_ids': list(self.product_ids)}

    def __eq__(self, other):
        if self.name != other.name:
            raise TypeError('Channels need the same name to be compared.')
        return (self.name == other.name and
                self.product_ids == other.product_ids)

    def __add__(self, other):
        if self.name != other.name:
            raise TypeError('Channels need the same name to be added.')
        return Channel(self.name, list(self.product_ids | other.product_ids))

    def __sub__(self, other):
        if self.name != other.name:
            raise TypeError('Channels need the same name to be subtracted.')
        product_ids = self.product_ids - other.product_ids
        if not product_ids:
            return None
        return Channel(self.name, list(product_ids))