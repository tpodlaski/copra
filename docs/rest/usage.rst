=====
Usage
=====

.. warning::

  Any references made below to specific aspects of the Coinbase Pro API such as the data structures returned by methods may be out of date. Please visit `Coinbase Pro's WebSocket REST API documentation <https://docs.pro.coinbase.com/#api/>`__ for the authorative and up to date API information.
  
Introduction
------------
:class:`copra.rest.Client`, the asyncronous REST client class provided by CoPrA, is intentionally simple. Its methods were designed specifically to replicate all of the endpoints offered by the Coinbase Pro REST service, both in the parameters they expect and the data they return. 

With very few exceptions there is a one to one correspondence between :class:`copra.rest.Client` methods and the Coinbase endpoints. As often as possible, parameter names were kept the same and the json-encoded lists and dicts returned by the API server are, in turn, returned by the client methods untouched. This makes it simple to cross reference the CoPrA source code and documentation with `Coinbase's API documentation <https://docs.pro.coinbase.com/#api/)>`_. 

Additionally, it should be relatively easy to extend the client in order to build finer grained ordering methods, sophisticated account management systems, and powerful market analytics tools.

Errors
------
While :class:`copra.rest.Client` takes a hands-off approach to the data returned from API server, it does involve itself while preparing the user-supplied method paramters that will become part of the REST request. Specifically, in instances where the client can identify that the provided parameters will return an error from the API server, it raises a descriptive :class:`ValueError` in order to avoid an unnecessary server call. 

For example, the client method :meth:`copra.rest.Client.market_order` has parameters for the amount of currency to purchase or sell, ``size``, and for the amount of quote currency to use for the transaction, ``funds``. For a market order, it is impossible to require both so if both are sent in the method call, the client raises a :class:`ValueError`.

The :class:`copra.rest.Client` API documentation details for each method in what instances :class:`ValueErrors` are raised.

copra.rest.APIRequestError
++++++++++++++++++++++++++

On the other hand, there will be times the client cannot tell ahead of time that an API request will return an error. Insufficient funds, invalid account ids, improper authorization, and internal server errors are just a few examples of the errors a request may return.

Because there are many potential error types, and the Coinbase documentation does not list them all, the :class:`copra.rest.Client` raises a generic error, :class:`copra.rest.APIRequestError`, whenever the HTTP status code of an API server response is non-2xx.

The string representation of an ``APIRequestError`` is the message returned by the Coinbase server along the HTTP status code. ``APIRequestError``, also has an additional field, ``response``, is the `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#response-object>`_ object returned to the CoPrA client by the aiohttp request. This can be used to get more information about the request/response including full headers, etc. See the `aiohttp.ClientResponse documentation <https://docs.aiohttp.org/en/stable/client_reference.html#response-object>`_ to learn more about its attributes.

To get a feel for the types of errors that the Coinbase server may return, please see the `Coinbase Pro API error documentation <https://docs.pro.coinbase.com/#errors>`_.

REST Client 
-----------

The CoPrA REST client methods like their respective Coinbase REST API endpoints fall in one of two main categories: public and private. Public methods require no authentication. They offer access to market data and other publically avaiable information. The private methods *do* require authentication, specifically by means of an API key.  To learn how to create an API key see the Coinbase Pro support article titled `"How do I create an API key for Coinbase Pro?" <https://support.pro.coinbase.com/customer/en/portal/articles/2945320-how-do-i-create-an-api-key-for-coinbase-pro->`_.

Initialization
++++++++++++++

.. automethod:: copra.rest.Client.__init__

Initialization of an unauthorized client only requires one parameter: the asyncio loop the client will be running in:

.. code:: python

    import asyncio

    from copra.rest import Client

    loop = asyncio.get_event_loop()

    client = Client(loop)
    
To initialize an authorized client you will also need the key, secret, passphrase that Coinbase provides you when you request an  API key:


.. code:: python

    import asyncio

    from copra.rest import Client

    loop = asyncio.get_event_loop()

    client = Client(loop, auth=True, key=YOUR_KEY, 
                    secret=YOUR_SECRET, passphrase=YOUR_PASSPHRASE)

Client Lifecycle
---------------

The lifecycle of a long-lived client is straight forward:

.. code:: python
    
    client = Client(loop)
    
    # Make a fortune trading Bitcoin here
    
    await client.close()
    
Initialize the client, make as many requests as you need to, and then close the client to release any resources the underlying aiohttp session acquired. Note that the Python interpreter will complain if your program closes without closing your client first.

If you need to close the client from a function that is not a coroutine and the loop is remaining open you can close it like so:

.. code:: python

    loop.create_task(client.close())
    
Or, if the loop is closing, use:

.. code:: python

    loop.run_until_complete(client.close())
    
Context Manager
---------------

If you only need to create a client, use it briefly and not need it again for the duraction of your program, you can create it as context manager in which case the client is closed automatically when program execution leave the context manager block:

.. code:: python

    async with Client(loop) as client:
        client.do_something()
        client.do_something_else()
        
Note that if you will be using the client repeatedly over the duration of your program, it is best to create one client, store a reference to it, and use it repeatedly instead of creating a new client every time you need to make a request or two. This has to do with the aiohttp session handles its connection pool. Connections are reused and keep-alives are on which will result in better performance in subsequent requests versus creating a new client every time.

Public (Unauthorized) Client Methods
--------------

Coinbase refers to the collection of endpoints that do not require authorization as their "Market Data API". They further group those endpoints into 3 categories: products, currency and time. The CoPra rest client provides methods that are a one-to-one match to the endpoints in Coinbase's Market Data API.

Products
++++++++

.. autoclass:: Client

   .. automethod:: products() 

Currency
++++++++

Time
++++

