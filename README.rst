CoPrA
=========================================

*Python Asyncronous WebSocket Client for Coinbase Pro*

| |Version| |Build Status| |Docs|

-----------------------------------------

| **Quick Links**: `Documentation <https://copra.readthedocs.io/en/latest/>`__ - `Source Code <https://github.com/tpodlaski/copra>`__

| **Related**: `Coinbase Pro Digital Currency Exchange <https://pro.coinbase.com/>`__ - `Coinbase Pro WebSocket API <https://docs.pro.coinbase.com/#websocket-feed>`__

Introduction
------------

CoPrA \(**Co**\ inbase **Pr**\ o **A**\ sync\) is an asyncronous websocket client written in Python for use with the **Coinbase Pro** digital currency trading platform. To learn about Coinbase Pro's websocket service including the available channels and the data they provide, please see `Coinbase Pro's Websocket API documentation <https://docs.pro.coinbase.com/#websocket-feed>`__.


Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.5 or greater
* Autobahn|Python

The base websocket functionality for CoPrA is provided by **Autobahn|Python**, the open-source (MIT) real-time framework for web, mobile & the Internet of Things.

If you install copra using pip, Autobahn will be installed automatically. To install Autobahn manually using pip::

    $ pip3 install autobahn

Autobahn can also be installed from source by downnloading the code from: https://github.com/crossbario/autobahn-python .


Installing
~~~~~~~~~~

The easiest way to install CoPrA (and its dependencies) is by using pip::

    $ pip3 install copra


Examples
~~~~~~~~

You will likely want to override ``copra.websocket.client``, but it can be used 'as is' to test the module through the command line::

    # example.py

    import asyncio
    import logging
    
    from copra.websocket import Channel, Client
    
    loop = asyncio.get_event_loop()

    ws = Client(loop, [Channel('heartbeat', 'BTC-USD')])

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()

Running the above::

    $ python3 example.py
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

CoPrA supports authentication allowing you to receive only messages specific to your user account. (NOTE: This requires registering an API key at Coinbase Pro)::

    # example2.py

    import asyncio
    import logging

    from copra.websocket import Channel, Client

    KEY = YOUR_KEY
    SECRET = YOUR_SECRET
    PASSPHRASE = YOUR_PASSPHRASE
    
    loop = asyncio.get_event_loop()

    channel = Channel('user', 'LTC-USD')

    ws = Client(loop, channel, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()
        

Running the above::

    $python3 example2.py
    {'type': 'subscriptions', 'channels': [{'name': 'user', 'product_ids': ['LTC-USD']}]}
    {'type': 'received', 'order_id': '42d2677d-0d37-435f-a776-e9e7f81ff22b', 'order_type': 'limit', 'size': '50.00000000', 'price': '1.00000000', 'side': 'buy', 'client_oid': '00098b59-4ac9-4ff8-ba16-bd2ef673f7b7', 'product_id': 'LTC-USD', 'sequence': 2311323871, 'user_id': '642394321fdf8343c4006432', 'profile_id': '039ff148-d490-45f9-9aed-0d1f6412884', 'time': '2018-07-07T17:33:29.755000Z'}
    {'type': 'open', 'side': 'buy', 'price': '1.00000000', 'order_id': '42d2677d-0d37-435f-a776-e9e7f81ff22b', 'remaining_size': '50.00000000', 'product_id': 'LTC-USD', 'sequence': 2311323872, 'user_id': '642394321fdf8343c4006432', 'profile_id': '039ff148-d490-45f9-9aed-0d1f6412884', 'time': '2018-07-07T17:33:29.755000Z'}
    .
    .
    .

Versioning
----------

We use SemVer_ for versioning. For the versions available, see the `tags on this repository`_.


License
-------

This project is licensed under the **MIT License** - see the `LICENSE`_ file for details


Authors
-------
**Tony Podlaski** - http://www.neuraldump.net 

See also the list of contributers_ who participated in this project.

Contributing
------------
Please read `CONTRIBUTING.rst`_ for details on our code of conduct, and the process for submitting pull requests to us.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.


.. |Version| image:: https://img.shields.io/pypi/v/copra.svg
   :target: https://pypi.python.org/pypi/copra
   
.. |Build Status| image:: https://img.shields.io/travis/tpodlaski/copra.svg
   :target: https://travis-ci.org/tpodlaski/copra
   
.. |Docs| image:: https://readthedocs.org/projects/copra/badge/?version=latest
   :target: https://copra.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   
.. _SemVer: http://semver.org/
.. _`tags on this repository`: https://github.com/tpodlaski/copra/tags
.. _`LICENSE`: https://github.com/tpodlaski/copra/blob/master/LICENSE
.. _contributers: https://github.com/tpodlaski/copra/blob/master/CONTRIBUTING.rst
.. _`CONTRIBUTING.rst`: https://github.com/tpodlaski/copra/blob/master/CONTRIBUTING.rst
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

