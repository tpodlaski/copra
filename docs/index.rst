=========================================
CoPrA
=========================================

*Asyncronous Python REST and WebSocket Clients for Coinbase Pro*

-----------------------------------------

| |Version| |Build Status| |Docs|

|

| **Quick Links**: `Documentation <https://copra.readthedocs.io/en/latest/>`__ - `Source Code <https://github.com/tpodlaski/copra>`__ - `PyPi <https://pypi.org/project/copra/>`__

| **Related**: `Coinbase Pro Digital Currency Exchange <https://pro.coinbase.com/>`__ - `Coinbase Pro REST API <https://docs.pro.coinbase.com/#api>`_ - `Coinbase Pro WebSocket API <https://docs.pro.coinbase.com/#websocket-feed>`_

-----------------------------------------

Introduction
------------

The CoPrA \(**Co**\ inbase **Pr**\ o **A**\ sync\) package provides asyncronous REST and WebSocket clients written in Python for use with the Coinbase Pro digital currency trading platform. To learn about Coinbase Pro's REST and WebSocket APIs as well as how to obtain an API key for authentication to those services, please see `Coinbase Pro's API documentation <https://docs.pro.coinbase.com/>`__.

CoPrA Features
--------------

* compatible with Python 3.5 or greater
* utilizes Python's `asyncio <https://docs.python.org/3/library/asyncio.html>`__ concurrency framework
* open source (`MIT <https://github.com/tpodlaski/copra/blob/master/LICENSE>`__ license)

REST Features
+++++++++++++

* Asyncronous REST client class with 100% of the account management, trading, and market data functionality offered by the Coinbase Pro REST API.
* supports user authentication
* built on **aiohttp**, the asynchronous HTTP client/server framework for asyncio and Python

WebSocket Features
++++++++++++++++++

* Asyncronous WebSocket client class with callback hooks for managing every phase of a Coinbase Pro WebSocket session
* supports user authentication
* built on **Autobahn|Python**, the open-source (MIT) real-time framework for web, mobile & the Internet of Things.

Examples
--------

REST
++++
Without a Coinbase Pro API key, ``copra.rest.Client`` has access to all of the public market data that Coinbase makes available.

.. code:: python

    # 24hour_stats.py

    import asyncio

    from copra.rest import Client

    loop = asyncio.get_event_loop()

    client = Client(loop)

    async def get_stats():
        btc_stats = await client.get_24hour_stats('BTC-USD')
        print(btc_stats)

    loop.run_until_complete(get_stats())
    loop.run_until_complete(client.close())

Running the above:

.. code:: bash

    $ python3 24hour_stats.py
    {'open': '3914.96000000', 'high': '3957.10000000', 'low': '3508.00000000', 'volume': '37134.10720409', 'last': '3670.06000000', 'volume_30day': '423047.53794129'}

In conjunction with a Coinbase Pro API key, ``copra.rest.Client`` can be used to trade cryptocurrency and manage your Coinbase pro account. This example also shows how  ``copra.rest.Client`` can be used as a context manager.

.. code:: python

    # btc_account_info.py

    import asyncio

    from copra.rest import Client

    KEY = YOUR_API_KEY
    SECRET = YOUR_API_SECRET
    PASSPHRASE = YOUR_API_PASSPHRASE

    BTC_ACCOUNT_ID = YOUR_BTC_ACCOUNT_ID

    loop = asyncio.get_event_loop()

    async def get_btc_account():
        async with Client(loop, auth=True, key=KEY, 
                          secret=SECRET, passphrase=PASSPHRASE) as client:

            btc_account = await client.account(BTC_ACCOUNT_ID)
            print(btc_account)

    loop.run_until_complete(get_btc_account())

Running the above:

.. code:: bash

    $ python3 btc_account_info.py
    {'id': '1b121cbe-bd4-4c42-9e31-7047632fc7c7', 'currency': 'BTC', 'balance': '26.1023109600000000', 'available': '26.09731096', 'hold': '0.0050000000000000', 'profile_id': '151d9abd-abcc-4597-ae40-b6286d72a0bd'}
    
WebSocket
+++++++++

While ``copra.websocket.Client`` is meant to be overridden, but it can be used 'as is' to test the module through the command line.

.. code:: python

    # btc_heartbeat.py

    import asyncio
    
    from copra.websocket import Channel, Client
    
    loop = asyncio.get_event_loop()

    ws = Client(loop, Channel('heartbeat', 'BTC-USD'))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()

Running the above:

.. code:: bash

    $ python3 btc_heartbeat.py
    {'type': 'subscriptions', 'channels': [{'name': 'heartbeat', 'product_ids': ['BTC-USD']}]}
    {'type': 'heartbeat', 'last_trade_id': 45950713, 'product_id': 'BTC-USD', 'sequence': 6254273323, 'time': '2018-07-05T22:36:30.823000Z'}
    {'type': 'heartbeat', 'last_trade_id': 45950714, 'product_id': 'BTC-USD', 'sequence': 6254273420, 'time': '2018-07-05T22:36:31.823000Z'}
    {'type': 'heartbeat', 'last_trade_id': 45950715, 'product_id': 'BTC-USD', 'sequence': 6254273528, 'time': '2018-07-05T22:36:32.823000Z'}
    {'type': 'heartbeat', 'last_trade_id': 45950715, 'product_id': 'BTC-USD', 'sequence': 6254273641, 'time': '2018-07-05T22:36:33.823000Z'}
    {'type': 'heartbeat', 'last_trade_id': 45950715, 'product_id': 'BTC-USD', 'sequence': 6254273758, 'time': '2018-07-05T22:36:34.823000Z'}
    {'type': 'heartbeat', 'last_trade_id': 45950720, 'product_id': 'BTC-USD', 'sequence': 6254273910, 'time': '2018-07-05T22:36:35.824000Z'}
    .
    .
    .

A Coinbase Pro API key allows ``copra.websocket.Client`` to authenticate with the Coinbase WebSocket server giving you access to feeds specific to your user account.

.. code:: python

    # user_channel.py

    import asyncio

    from copra.websocket import Channel, Client

    KEY = YOUR_API_KEY
    SECRET = YOUR_API_SECRET
    PASSPHRASE = YOUR_API_PASSPHRASE
    
    loop = asyncio.get_event_loop()

    channel = Channel('user', 'LTC-USD')

    ws = Client(loop, channel, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()
        

Running the above:

.. code:: bash

    $ python3 user_channel.py
    {'type': 'subscriptions', 'channels': [{'name': 'user', 'product_ids': ['LTC-USD']}]}
    {'type': 'received', 'order_id': '42d2677d-0d37-435f-a776-e9e7f81ff22b', 'order_type': 'limit', 'size': '50.00000000', 'price': '1.00000000', 'side': 'buy', 'client_oid': '00098b59-4ac9-4ff8-ba16-bd2ef673f7b7', 'product_id': 'LTC-USD', 'sequence': 2311323871, 'user_id': '642394321fdf8242c4006432', 'profile_id': '039ee148-d490-44f9-9aed-0d1f6412884', 'time': '2018-07-07T17:33:29.755000Z'}
    {'type': 'open', 'side': 'buy', 'price': '1.00000000', 'order_id': '42d2677d-0d37-435f-a776-e9e7f81ff22b', 'remaining_size': '50.00000000', 'product_id': 'LTC-USD', 'sequence': 2311323872, 'user_id': '642394321fdf8242c4006432', 'profile_id': '039ee148-d490-44f9-9aed-0d1f6412884', 'time': '2018-07-07T17:33:29.755000Z'}
    .
    .
    .

.. |Version| image:: https://img.shields.io/pypi/v/copra.svg
   :target: https://pypi.python.org/pypi/copra
   
.. |Build Status| image:: https://img.shields.io/travis/tpodlaski/copra.svg
   :target: https://travis-ci.org/tpodlaski/copra
   
.. |Docs| image:: https://readthedocs.org/projects/copra/badge/?version=latest
   :target: https://copra.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
