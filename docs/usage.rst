=====
Usage
=====

.. warning::

  Any references made below to specific aspects of the Coinbase Pro API such as the channels and the data they provide may be out of date. Please visit `Coinbase Pro's WebSocket API documentation <https://docs.pro.coinbase.com/#websocket-feed/> for the authorative and up to date information.
  
Introduction
------------

The CoPrA API provides two classes for creating a WebSocket client for the Coinbase Pro platform. The first, ``copra.websocket.Channel``, is intended to be used "as is." The second, ``copra.websocket.Client``, is the actual client class. It provides multiple callback methods to manage every stage of the client's life cycle.

Channel
-------

At the heart of every WebSocket connection is the concept of a channel. 
