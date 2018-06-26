# -*- coding: utf-8 -*-
"""Asynchronous websocket client for the Coinbase Pro platform.

"""


class Channel:
    """A websocket channel.

    A Channel object encapsulates the Coinbase Pro websocket channel name
    *and* one or more Coinbase Pro product ids.

    To read about Coinbase Pro channels and the data they return, visit:
    https://docs.gdax.com/#channels

    Attributes:
        name (str): The name of the websocket channel.

    """

    def __init__(self, name):
        """Channel __init__ method.

        Args:
            name (str): The name of the websocket channel. Possible values
                are heatbeat, ticker, level2, full, matches, or user

            product_ids (str or list of str): A single product id
                (eg., 'BTC-USD') or list of product ids (eg., ['BTC-USD',
                'ETH-EUR', 'LTC-BTC'])

        """
        self.name = name.lower()
        if self.name not in ('heartbeat', 'ticker', 'level2',
                             'full', 'matches', 'user'):
            raise ValueError("invalid name {}".format(name))
