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
    """

    def __init__(self, loop, channels, feed_url=FEED_URL,
                 auth=False, key='', secret='', passphrase='',
                 auto_connect=True, auto_reconnect=True,
                 name='WebSocket Client'):
        """
        
        :param loop: The asyncio loop that the client runs in.
        :type loop: asyncio loop
        
        :param channels: The channels to initially subscribe to.
        :type channels: Channel or list of Channels
        
        :param str feed_url:  The url of the WebSocket server. The defualt is
            copra.WebSocket.FEED_URL (wss://ws-feed.gdax.com)
            
        :param bool auth:  Whether or not the (entire) WebSocket session is
            authenticated. If True, you will need an API key from the
            Coinbase Pro website. The default is False.
            
        :param str key:  The API key to use for authentication. Required if auth
            is True. The default is ''.
            
        :param str secret: The secret string for the API key used for
            authenticaiton. Required if auth is True. The default is ''.
            
        :param str passphrase: The passphrase for the API key used for
            authentication. Required if auth is True. The default is ''.

        :param bool auto_connect: If True, the Client will automatically add
            itself to its event loop (ie., open a connection if the loop is
            running or as soon as it starts). If False, add_as_task_to_loop()
            needs to be explicitly called to add the client to the loop. The
            default is True.
            
        :param bool auto_reconnect: If True, the Client will attemp to autom-
            matically reconnect and resubscribe if the connection is closed any
            way but by the Client explicitly itself. The default is True.
                
        :param str name: A name to identify this client in logging, etc.
        
        :raises ValueError: If auth is True and key, secret, and passphrase are
            not provided.
        """

        self.loop = loop
        
        self.connected = asyncio.Event()
        self.disconnected = asyncio.Event()
        self.disconnected.set()
        self.closing = False
        
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
        self.auto_reconnect = auto_reconnect
        self.name = name

        super().__init__(self.feed_url)
        
        if self.auto_connect:
            self.add_as_task_to_loop()

    def _get_subscribe_message(self, channels, unsubscribe=False, timestamp=None):
        """Create and return the subscription message for the provided channels.
        
        :param channels: List of channels to be subscribed to.
        :type channels: list of Channel
        
        :param bool unsubscribe:  If True, returns an unsubscribe message
            instead of a subscribe method. The default is False.

        :returns: JSON-formatted, UTF-8 encoded bytes object representing the
            subscription message for the provided channels.
        """
        msg_type = 'unsubscribe' if unsubscribe else 'subscribe'
        msg = {'type': msg_type,
               'channels': [channel._as_dict() for channel in channels]}

        if self.auth:
            if not timestamp:
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

    def subscribe(self, channels):
        """Subscribe to the given channels.
        
        :param channels: The channels to subscribe to.
        :type channels: Channel or list of Channels
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

        if self.connected.is_set():
            msg = self._get_subscribe_message(sub_channels)
            self.protocol.sendMessage(msg)

    def unsubscribe(self, channels):
        """Unsubscribe from the given channels. 
        
        :param channels: The channels to subscribe to.
        :type channels: Channel or list of Channels
        """
        if not isinstance(channels, list):
            channels = [channels]

        for channel in channels:
            if channel.name in self.channels:
                self.channels[channel.name] -= channel
                if not self.channels[channel.name]:
                    del self.channels[channel.name]

        if self.connected.is_set():
            msg = self._get_subscribe_message(channels, unsubscribe=True)
            self.protocol.sendMessage(msg)

    def add_as_task_to_loop(self):
        """Add the client to the asyncio loop.

        Creates a coroutine for making a connection to the WebSocket server and
        adds it as a task to the asyncio loop.
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
        self.connected.set()
        self.disconnected.clear()
        self.closing = False
        logger.info('{} connected to {}'.format(self.name, self.url))
        msg = self._get_subscribe_message(self.channels.values())
        self.protocol.sendMessage(msg)

    def on_close(self, was_clean, code, reason):
        """Callback fired when the WebSocket connection has been closed.

        (WebSocket closing handshake has been finished or the connection was
        closed uncleanly).
        
        :param bool was_clean: True iff the WebSocket connection closed cleanly.
        
        :param code: Close status code as sent by the WebSocket peer.
        :type code: int or None
        
        :param reason: Close reason as sent by the WebSocket peer.
        :type reason: str or None
        """
        self.connected.clear()
        self.disconnected.set()

        msg = '{} connection to {} {}closed. {}'
        expected = 'unexpectedly ' if self.closing is False else ''

        logger.info(msg.format(self.name, self.url, expected, reason))

        if not self.closing and self.auto_reconnect:
            msg = '{} attempting to reconnect to {}.'
            logger.info(msg.format(self.name, self.url))

            self.add_as_task_to_loop()

    def on_error(self, message, reason=''):
        """Callback fired when an error message is received.
        
        :param str message: A general description of the error.
        :param str reason:  A more detailed description of the error.

        """
        logger.error('{}. {}'.format(message, reason))

    def on_message(self, message):
        """Callback fired when a complete WebSocket message was received.

        You will likely want to override this method.
        
        :param dict message: Dictionary representing the message.
        """
        print(message)

    async def close(self):
        """Close the WebSocket connection.
        """
        self.closing = True
        self.protocol.sendClose()
        await self.disconnected.wait()

if __name__ == '__main__':
    # A sanity check.

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())

    loop = asyncio.get_event_loop()

    ws = Client(loop, [Channel('heartbeat', 'BTC-USD')])

    async def add_a_channel():
        await asyncio.sleep(20)
        ws.subscribe(Channel('heartbeat', 'LTC-USD'))
        loop.create_task(remove_a_channel())

    async def remove_a_channel():
        await asyncio.sleep(20)
        ws.unsubscribe(Channel('heartbeat', 'BTC-USD'))

    loop.create_task(add_a_channel())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()
