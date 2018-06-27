# -*- coding: utf-8 -*-
"""Asynchronous websocket client for the Coinbase Pro platform.

"""

import logging

logger = logging.getLogger(__name__)


class Channel:
    """A websocket channel.

    A Channel object encapsulates the Coinbase Pro websocket channel name
    *and* one or more Coinbase Pro product ids.

    To read about Coinbase Pro channels and the data they return, visit:
    https://docs.gdax.com/#channels

    Attributes:
        name (str): The name of the websocket channel.
        product_ids (list of str): List of product ids for the channel.

    """

    def __init__(self, name, product_ids):
        """Channel __init__ method.

        Args:
            name (str): The name of the websocket channel. Possible values
                are heatbeat, ticker, level2, full, matches, or user

            product_ids (str or list of str): A single product id
                (eg., 'BTC-USD') or list of product ids (eg., ['BTC-USD',
                'ETH-EUR', 'LTC-BTC'])

        Raises:
            ValueError: If name not valid or product ids is empty.

        """
        self.name = name.lower()
        if self.name not in ('heartbeat', 'ticker', 'level2',
                             'full', 'matches', 'user'):
            raise ValueError("invalid name {}".format(name))

        if not product_ids:
            raise ValueError("must include at least one product id")

        if not isinstance(product_ids, list):
            product_ids = [product_ids]
        self.product_ids = product_ids

    def as_dict(self):
        """Returns the Channel as a dictionary.

        Returns:
            dict: The Channel as a dict with keys name & product_ids.
        """
        return {'name': self.name, 'product_ids': self.product_ids}
