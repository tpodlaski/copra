=====
Usage
=====

.. warning::

  Any references made below to specific aspects of the Coinbase Pro API such as the channels and the data they provide may be out of date. Please visit `Coinbase Pro's WebSocket API documentation <https://docs.pro.coinbase.com/#websocket-feed/> for the authorative and up to date information.
  
Introduction
------------

The CoPrA API provides two classes for creating a WebSocket client for the Coinbase Pro platform. The first, ``copra.websocket.Channel``, is intended to be used "as is." The second, ``copra.websocket.Client``, is the actual client class. It provides multiple callback methods to manage every stage of the client's life cycle.

Channel* 
-------

At the heart of every WebSocket connection is the concept of a channel. A channel provides a specific type of data 
about one or more currency pairs. ``copra.websocket.Channel`` has two attributes: it's name ``name`` and the product pairs the channel is observing, ``product_ids``.

The current channels provided by the Coinbase Pro API are:

* **heartbeart** - heartbeat messages are generated once a second include sequence numbers and last trade ids that can be used to verify no messages were missed.

* **ticker** - ticker messages are sent every time a match happens providing real-time price updates.

* **level2** - level2 messages provide a high level view of the order book. After the initial snapshot of the order book is delivered, messages are sent every time the volume at specific price tier on the buy or sell side changes.

* **full** - the full channel provides real-time updates on orders and trades. There are messages for every stage of an orders life cycle including: received, open, match, done, change, and activate.

* **user** - the user channel provides the same information as the full channel but only for the authenticated user. As such you will need to be authenticated to susbsribe. This requires a Coinbase Pro API key.

* **matches** - this channel consists only of the match messages from the full channel.

