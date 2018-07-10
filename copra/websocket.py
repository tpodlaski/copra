# -*- coding: utf-8 -*-
"""Asynchronous WebSocket client for the Coinbase Pro platform.

"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import time
from urllib.parse import urlparse

from autobahn.asyncio.websocket import WebSocketClientFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol

logger = logging.getLogger(__name__)

FEED_URL = 'wss://ws-feed.pro.coinbase.com:443'
SANDBOX_FEED_URL = 'wss://ws-feed-public.sandbox.pro.coinbase.com:443'


class Channel:
    """A WebSocket channel.

    A Channel object encapsulates the Coinbase Pro WebSocket channel name
    *and* one or more Coinbase Pro product ids.

    To read about Coinbase Pro channels and the data they return, visit:
    https://docs.gdax.com/#channels

    Attributes:
        name (str): The name of the WebSocket channel.
        product_ids (set of str): Set of product ids for the channel.

    """

    def __init__(self, name, product_ids):
        """Channel __init__ method.

        Args:
            name (str): The name of the WebSocket channel. Possible values
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
        self.product_ids = set(product_ids)

    def as_dict(self):
        """Returns the Channel as a dictionary.

        Returns:
            dict: The Channel as a dict with keys name & product_ids.
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


class ClientProtocol(WebSocketClientProtocol):
    """Websocket client protocol.

    This is a subclass of autobahn.asyncio.WebSocket.WebSocketClientProtocol.
    In most cases this should not need to be subclassed or even accessed
    directly.
    """

    def __call__(self):
        return self

    def onOpen(self):
        """Callback fired on initial WebSocket opening handshake completion.

        You now can send and receive WebSocket messages.
        """
        self.factory.on_open()

    def onClose(self, wasClean, code, reason):
        """Callback fired when the WebSocket connection has been closed.

        (WebSocket closing handshake has been finished or the connection was
        closed uncleanly).

        Args:
          wasClean (bool): True iff the WebSocket connection closed cleanly.
          code (int or None): Close status code as sent by the WebSocket peer.
          reason (str or None): Close reason as sent by the WebSocket peer.
        """
        self.factory.on_close(wasClean, code, reason)

    def onMessage(self, payload, isBinary):
        """Callback fired when a complete WebSocket message was received.

        Call its factory's (the client's) on_message method with a
        dict representing the JSON message receieved.

        Args:
            payload (bytes): The WebSocket message received.
            isBinary (bool): Flag indicating whether payload is binary or UTF-8
            encoded text.
        """
        msg = json.loads(payload.decode('utf8'))
        if msg['type'] == 'error':
            self.factory.on_error(msg['message'], msg.get('reason', ''))
        else:
            self.factory.on_message(msg)


class Client(WebSocketClientFactory):
    """Asyncronous WebSocket client for Coinbase Pro.

       Attributes:
           feed_url (str): The url of the WebSocket server.
    """

    def __init__(self, loop, channels, feed_url=FEED_URL,
                 auth=False, key='', secret='', passphrase='',
                 auto_connect=True, name='WebSocket Client'):
        """ Client initialization.

        Args:
            loop (asyncio loop): The asyncio loop that the client runs in.
            channels (Channel or list of Channel): The initial channels to
                initially subscribe to.
            feed_url (str): The url of the WebSocket server. The defualt is
                copra.WebSocket.FEED_URL (wss://ws-feed.gdax.com)
            auth (bool): Whether or not the (entire) WebSocket session is
                authenticated. If True, you will need an API key from the
                Coinbase Pro website. The default is False.
            key (str): The API key to use for authentication. Required if auth
                is True. The default is ''.
            secret (str): The secret string for the API key used for
                authenticaiton. Required if auth is True. The default is ''.
            passphrase (str): The passphrase for the API key used for
                authentication. Required if auth is True. The default is ''.
            auto_connect (bool): If True, the Client will automatically add
                itself to its event loop (ie., open a connection if the loop
                is running or as soon as it starts). If False,
                add_as_task_to_loop() needs to be explicitly called to add the
                client to the loop.
            name (str): A name to identify this client in logging, etc.


        Raises:
            ValueError: If auth is True and key, secret, and passphrase are
                not provided.
        """
        self.connected = False
        self.loop = loop
        if not isinstance(channels, list):
            channels = [channels]

        self._initial_channels = channels
        self.feed_url = feed_url

        self.channels = {}
        self.subscribe(channels)

        if auth and not (key and secret and passphrase):
            raise ValueError('auth requires key, secret, and passphrase')

        self.auth = auth
        self.key = key
        self.secret = secret
        self.passphrase = passphrase

        self.auto_connect = auto_connect
        self.name = name

        super().__init__(self.feed_url)

        if self.auto_connect:
            self.add_as_task_to_loop()

    def subscribe(self, channels):
        """Subscribe to the given channels.

        Params:
            channels (Channel or list of Channels): The channels to subscribe
                to.
        """
        if not isinstance(channels, list):
            channels = [channels]

        sub_channels = []

        for channel in channels:
            if channel.name in self.channels:
                sub_channel = channel - self.channels[channel.name]
                if sub_channel:
                    self.channels[channel.name] += channel
                    sub_channels.append(sub_channel)

            else:
                self.channels[channel.name] = channel
                sub_channels.append(channel)

        if self.connected:
            pass
        else:
            # The client isn't currently connected. self.channels has been
            # updated and a subscribe message for them will be sent on_open.
            pass

    def get_subscribe_message(self, channels):
        """Create and return the subscription message for the provided channels.

        Args:
            channels (list of Channel): List of channels to subscribe to.

        Returns:
            bytes: JSON-formatted, UTF-8 encoded bytes object representing the
                subscription message for the provided channels.
        """
        msg = {'type': 'subscribe',
               'channels': [channel.as_dict() for channel in channels]}

        if self.auth:
            timestamp = str(time.time())
            message = timestamp + 'GET' + '/users/self/verify'
            message = message.encode('ascii')
            hmac_key = base64.b64decode(self.secret)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest())
            signature_b64 = signature_b64.decode('utf-8').rstrip('\n')

            msg['signature'] = signature_b64
            msg['key'] = self.key
            msg['passphrase'] = self.passphrase
            msg['timestamp'] = timestamp

        return json.dumps(msg).encode('utf8')

    def add_as_task_to_loop(self):
        """Add the client to the asyncio loop.

        Creates a coroutine for making a connection to the WebSocket server and
        adds it as a task to the asyncio loop.

        Args:
            loop (asyncio event loop): The event loop that the WebSocket client
                runs in.
        """
        self.protocol = ClientProtocol()
        url = urlparse(self.url)
        self.coro = self.loop.create_connection(self, url.hostname, url.port,
                                                ssl=(url.scheme == 'wss'))
        self.loop.create_task(self.coro)

    def on_open(self):
        """Callback fired on initial WebSocket opening handshake completion.

        The WebSocket is open. This method sends the subscription message to
        the server.
        """
        self.connected = True
        logger.info('{} connected to {}'.format(self.name, self.url))
        msg = self.get_subscribe_message(self.channels.values())
        self.protocol.sendMessage(msg)

    def on_close(self, was_clean, code, reason):
        """Callback fired when the WebSocket connection has been closed.

        (WebSocket closing handshake has been finished or the connection was
        closed uncleanly).

        Args:
          was_clean (bool): True iff the WebSocket connection closed cleanly.
          code (int or None): Close status code as sent by the WebSocket peer.
          reason (str or None): Close reason as sent by the WebSocket peer.
        """
        self.connected = False
        logger.info('Connection to {} closed. {}'.format(self.url, reason))

    def on_error(self, message, reason=''):
        """Callback fired when an error message is received.

        Args:
            message (str): A general description of the error.
            reason (str): A more detailed description of the error.
        """
        logger.error('{}. {}'.format(message, reason))

    def on_message(self, msg):
        """Callback fired when a complete WebSocket message was received.

        You will likely want to override this method.

        Args:
            msg (dict): Dictionary representing the message.
        """
        print(msg)

    async def close(self):
        """Close the WebSocket connection.
        """
        self.protocol.sendClose()


if __name__ == '__main__':

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())

    loop = asyncio.get_event_loop()

    ws = Client(loop, [Channel('heartbeat', 'BTC-USD')])

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()
