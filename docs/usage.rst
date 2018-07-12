=====
Usage
=====

.. warning::

  Any references made below to specific aspects of the Coinbase Pro API such as the channels and the data they provide may be out of date. Please visit `Coinbase Pro's WebSocket API documentation <https://docs.pro.coinbase.com/#websocket-feed/>`__ for the authorative and up to date information.
  
Introduction
------------

The CoPrA API provides two classes for creating a WebSocket client for the Coinbase Pro platform. The first, ``copra.websocket.Channel``, is intended to be used "as is." The second, ``copra.websocket.Client``, is the actual client class. It provides multiple callback methods to manage every stage of the client's life cycle.

Channel
-------

At the heart of every WebSocket connection is the concept of a channel. A channel provides a specific type of data 
about one or more currency pairs. ``copra.websocket.Channel`` has two attributes: it's name ``name`` and the product pairs the channel is observing, ``product_ids``.

The current channels provided by the Coinbase Pro API are:

* **heartbeart** - heartbeat messages are generated once a second. They include sequence numbers and last trade IDs that can be used to verify no messages were missed.

* **ticker** - ticker messages are sent every time a match happens providing real-time price updates.

* **level2** - level2 messages provide a high level view of the order book. After the initial snapshot of the order book is delivered, messages are sent every time the volume at specific price tier on the buy or sell side changes.

* **full** - the full channel provides real-time updates on orders and trades. There are messages for every stage of an orders life cycle including: received, open, match, done, change, and activate.

* **user** - the user channel provides the same information as the full channel but only for the authenticated user. As such you will need to be authenticated to susbsribe. This requires a Coinbase Pro API key.

* **matches** - this channel consists only of the match messages from the full channel.

The Coinbase Pro exchange currently hosts four digital currencies:

* **BTC** - Bitcoin
* **BCH** - Bitcoin Cash
* **ETH** - Etherium
* **LTC** - Litecoin Cash

And allows 3 fiat currencies for trading:

* **USD** - US Dollar
* **EUR** - Euro
* **GBP** - Great British Pounds (Sterling)

Not every combination of currencies is available for trading, however. The current currency pairs (or products) avaialable for trade are:

* **BTC-USD**
* **BTC-EUR**
* **BTC-GBP**
* **ETH-USD**
* **ETH-EUR**
* **ETH-BTC**
* **LTC-USD**
* **LTC-EUR**
* **LTC-BTC**
* **BCH-USD**
* **BCH-EUR**
* **BCH-BTC**

These are the product IDs referenced below.

Before connecting to the Coinbase Pro Websocket server, you will need to create one or more channels to subscribe to.

First, import the ``Channel`` class:

.. code:: python

    from copra.websocket import Channel
    
The channel is then initialized with its name and one or more product IDs. The heartbeat channel for the Bitcoin/US dollar pair would be initialized:

.. code:: python

    channel = Channel('heartbeat', 'BTC-USD')
    
A channel that recieves ticker information about the pairs Etherium/US dollar and Litecoin/Euro would be initialized:

.. code:: python

    channel = Channel('ticker', ['ETH-USD', 'LTC-EUR'])
    
As illustrated above, the product ID argument to the ``Channel`` constructor can be a single string or a list of strings.

To listen for messages about Bitcoin/US Dollar and Litecoin/Bitcoin orders for an authenticated user:

.. code:: python

    channel = Channel('user', ['BTC-USD', 'LTC-BTC'])
    
As noted above, this will require that the ``Client`` be authenticated. This is covered below.

Client
------
The ``Client`` class represents the Coinbase Pro WebSocket client. While it can be used "as is", most developers will want to subclass it in order to customize the behavior of its callback methods.

First it needs to be imported:

.. code:: python

    from copra.websocket import Client
    
For reference, the signature of the ``Client`` ``__init__`` method is:

.. code:: python

    def __init__(self, loop, channels, feed_url=FEED_URL,
                 auth=False, key='', secret='', passphrase='',
                 auto_connect=True, auto_reconnect=True,
                 name='WebSocket Client')
                 
Only two parameters are required to create a client: ``loop`` and ``channels``.

``loop`` is the Python asyncio loop that the client will run in. Somewhere in your code you will likely have something like:

.. code:: python

    import asyncio
    
    loop = asyncio.get_event_loop()
    
``channels`` is either a single ``Channel`` or a list of ``Channels`` the client should immediately subscribe to.

``feed_url`` is the url of the Coinbase Pro Websocket server. The default is ``copra.websocket.FEED_URL`` which is wss://ws-feed.pro.coinbase.com:443. 

If you want to test your code in Coinbase's "sandbox" development environment, you can set ``feed_url`` to ``copra.websocket.SANDBOX_FEED_URL`` which is wss://ws-feed-public.sandbox.pro.coinbase.com:443.

``auth`` indicates whether or not the client will be authenticated. If True, you will need to also provide ``key``, ``secret``, and ``passphrase``. These values are provided by Coinbase Pro when you register for an API key.

``auto_connect`` determines whether or not to automatically add the client to the asyncio loop. If true, the client will be added to the loop when it (the client) is initialized. If the loop is already running, the WebSocket connection will open. If the loop is not yet running, the connection will be made as soon as the loop is started.

If ``auto_connect`` is False, you will need to explicitly call ``client.add_as_task_to_loop()`` when you are ready to add the client to the asyncio loop and open the WebSocket connection.

``auto_reconnect`` determines the client's behavior is the connection is closed in any way other than by explicitly calling its ``close`` method. If True, the client will automatically try to reconnect and re-subscribe to the channels it subscribed to when the connection unexpectedly closed.

``name`` is a simple string representing the name of the client. Setting this to something unique may be useful for logging purposes.

Callback Methods
~~~~~~~~~~~~~~~~

The ``Client`` class provides four methods that are automatically called at different stages of the client's life cycle. The method that will be most useful for developers is ``on_message()``.

on_open()
^^^^^^^^^

``on_open`` is called as soon as the initial WebSocket opening handshake is complete. The connection is open, but the client is **not yet subscribed**.

If you override this method it is important that **you still call it** from your subclass' ``on_open`` method, since the parent method sends the initial subscription request to the WebSocket server. Somewhere in your ``on_open`` method you should have ``super().on_open()``.

In addition to sending the subsciption request, this method also logs that the connection was opened.

on_message(message)
^^^^^^^^^^^^^^^^^^^

``on_message`` is called everytime a message is received. ``message`` is a dict representing the message. Its content will depend on the type of message, the channels subscribed to, etc. Please read `Coinbase Pro's WebSocket API documentation <https://docs.pro.coinbase.com/#websocket-feed/>`__ to learn about these message formats.

Note that with the exception of errors, every other message triggers this method including things like subscription confirmations. Your code should be prepared to handle unexpected messages. 

This default method just prints the message received. If you override this method, there is no need to call the parent method from your subclass' method.

on_error(message, reason)
^^^^^^^^^^^^^^^^^^^^^^^^

``on_error`` is called when an error message is received from the WebSocket server. ``message`` a is string representing the error, and ``reason`` is a string that provides additional information about the cause of the error. Note that in many cases ``reason`` is blank.

The default implementation just logs the message and reason. If you override this method, your subclass only needs to call the parent's method if want to preserve this logging behavior.

on_close( was_clean, code, reason)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``on_close`` is called whenever the connection between the client and server is closed. ``was_clean`` is a boolean indicating whether or not the connection was cleanly closed. ``code``, an integer, and ``reason``, a string, are sent by the end that initiated closing the connection.

If the client did not initiate this closure and ``client.auto_reconnect`` is set to True, the client will attempt to reconnect to the server and resubscribe to the channels it was subscribed to when the connection was closed. This method also logs the closure.

If your subclass overrides this method, it is important that the subclass method calls the parent method if you want to preserve the auto reconnect functionality. This can be done by including ``super().on_close(was_clean, code, reason)`` in your subclass method.

Other Methods
~~~~~~~~~~~~~

close()
^^^^^^^

``close`` is called to close the connection to the WebSocket server. Note that if you call this method, the client will not attempt to auto reconnect regardless of what the value of ``client.auto_reconnect`` is.

subscribe(channels)
^^^^^^^^^^^^^^^^^^^

`subscribe` is called to susbcribe to additional channels. ``channels`` is either a single Channel or a list of Channels.

The original channels to be subscribed to are defined during the client's initialization. ``subscribe`` can be used to add channels whether the client has been added to asyncio loop yet or not. If the loop isn't yet running, the client will subscribe to all of its channels when it is. If the loop is already running, the subcription will be appended with new channels, and incoming data will be immediately received.

unsubscribe(channels)
^^^^^^^^^^^^^^^^^^^^^

``unsubscribe`` is called to unsubscribe from channels. ``channels`` is either a single Channel or a list of Channels.

Like ``subscribe``, ``unsubscribe`` can be called regardless of whether or not the client has already been added to the asyncio loop. If the client has not yet been added, ``unsubscribe`` will remove those channels from the set of channels to be initially subscribed to. If the client has already been added to the loop, ``unsubscribe`` will remove those channels from the subscription, and data flow from them will stop immediately.       
