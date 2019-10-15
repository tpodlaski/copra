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

``__init__(loop, url=URL, auth=False, key='', secret='', passphrase='')`` [:meth:`API Documentation <copra.rest.Client.__init__>`]

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

Public (Unauthenticated) Client Methods
--------------

Coinbase refers to the collection of endpoints that do not require authorization as their "Market Data API". They further group those endpoints into 3 categories: products, currency and time. The CoPra rest client provides methods that are a one-to-one match to the endpoints in Coinbase's Market Data API.

Products
++++++++

*
    | ``products()`` [:meth:`API Documentation <copra.rest.Client.products>`]
    | Get a list of available currency pairs for trading.

*
    | ``order_book(product_id, level=1)`` [:meth:`API Documentation <copra.rest.Client.order_book>`]
    | Get a list of open orders for a product.
    
*
    | ``ticker(product_id)`` [:meth:`API Documentation <copra.rest.Client.ticker>`]
    | Get information about the last trade for a product.
    
*
    | ``trades(product_id, limit=100, before=None, after=None)``  [:meth:`API Documentation <copra.rest.Client.trades>`]
    | List the latest trades for a product.
    
*
    | ``historic_rates(product_id, granularity=3600, start=None, stop=None)`` [:meth:`API Documentation <copra.rest.Client.historic_rates>`]
    | Get historic rates for a product.
    
*
    | ``get_24hour_stats(product_id)`` [:meth:`API Documentation <copra.rest.Client.get_24hour_stats>`]
    | Get 24 hr stats for a product.
    
Currency
++++++++

*
    | ``currencies()`` [:meth:`API Documentation <copra.rest.Client.currencies>`]
    | List known currencies.

Time
++++

*
    | ``server_time`` [:meth:`API Documentation <copra.rest.Client.server_time>`]
    | Get the API server time.


Private (Authenticated) Client Methods
--------------------------------------

Coinbase labels its REST endpoints for account and order management as "private." Private in this sense means that they require authentication with the API server by signing all requests with a Coinbase API key. To use the corresponding ``copra.rest.Client`` methods you will need your own Coinbase API key. To learn how to create an API key see the Coinbase Pro support article titled `"How do I create an API key for Coinbase Pro?" <https://support.pro.coinbase.com/customer/en/portal/articles/2945320-how-do-i-create-an-api-key-for-coinbase-pro->`_

Then you will need to initialize ``copra.rest.Client`` with that API key:


.. code:: python

    import asyncio

    from copra.rest import Client

    loop = asyncio.get_event_loop()

    client = Client(loop, auth=True, key=YOUR_KEY, 
                    secret=YOUR_SECRET, passphrase=YOUR_PASSPHRASE)
                    
.. Note:: Even if you have created an authenticated client, it will only sign the requests to the Coinbase API server that require authentication. The "public" market data methods will still be made unsigned.

The Coinbase API documentation groups the "private" authenticated methods into these categories: accounts, orders, fills, deposits, withdrawals, stablecoin conversions, payment methods, Coinbase accounts, reports, and user account.

Again there is a one-to-one mapping from ``copra.rest.Client`` methods and their respective Coinbase API endpoints, but this time there is one exception. Coinbase has a single endpoint, "/orders" for placing orders. This enpoint handles both limit and market orders as well as the stop versions of both. Because of the number of parameters needed to cover all types of orders as well as the complicated interactions between the them, the decision was made to split this enpoint into two methods: :meth:`copra.rest.Client.limit_order` and :meth:`copra.rest.Client.market_order`.

Accounts
++++++

*
    | ``accounts()`` [:meth:`API Documentation <copra.rest.Client.accounts>`]
    | Get a list of your Coinbase Pro trading accounts.
    
*
    | ``account(account_id)`` [:meth:`API Documentation <copra.rest.Client.accounts>`]
    | Retrieve information for a single account.
    
*
    | ``account_history(account_id, limit=100, before=None, after=None)`` [:meth:`API Documentation <copra.rest.Client.account_history>`]
    | Retrieve a list account activity.
    
*
    | ``holds(account_id, limit=100, before=None, after=None)`` [:meth:`API Documentation <copra.rest.Client.account_holds>`]
    | Get any existing holds on an account.

Orders
++++++

*
    | ``limit_order(side, product_id, price, size, time_in_force='GTC', cancel_after=None, post_only=False, client_oid=None, stp='dc',stop=None, stop_price=None)`` [:meth:`API Documentation <copra.rest.Client.limit_order>`]
    | Place a limit order or a stop entry/loss limit order.
    
*
    | ``market_order(self, side, product_id, size=None, funds=None, client_oid=None, stp='dc', stop=None, stop_price=None)`` [:meth:`API Documentation <copra.rest.Client.market_order>`]
    | Place a market order or a stop entry/loss market order.
    
*
    | ``cancel(order_id)`` [:meth:`API Documentation <copra.rest.Clientcancel>`]
    | Cancel a previously placed order.

*
    | ``cancel_all(product_id=None, stop=False)`` [:meth:`API Documentation <copra.rest.Clientcancel_all>`]
    | Cancel "all" orders.
    
*
    | ``orders(status=None, product_id=None, limit=100, before=None, after=None)`` [:meth:`API Documentation <copra.rest.Client.orders>`]
    | Retrieve a list orders
    
*
    | ``get_order(self, order_id)`` [:meth:`API Documentation <copra.rest.Client.get_order>`]
    | Get a single order by order id.
    
Fills       
+++++

*
    | ``fills(order_id='', product_id='', limit=100, before=None, after=None)`` [:meth:`API Documentation <copra.rest.Client.fills>`]
    | Get a list of recent fills.

Deposits
++++++++

*
    | ``deposit_payment_method(amount, currency, payment_method_id)`` [:meth:`API Documentation <copra.rest.Client.deposit_payment_method>`]
    | Deposit funds from a payment method on file.
    
*
    | ``deposit_coinbase(amount, currency, coinbase_account_id)`` [:meth:`API Documentation <copra.rest.Client.deposit_coinbase>`]
    | Deposit funds from a Coinbase account.

Withdrawals
+++++++++++

*
    | ``withdraw_payment_method(self, amount, currency, payment_method_id)`` [:meth:`API Documentation <copra.rest.Client.withdraw_payment_method>`]
    | Withdraw funds to a payment method on file.
    
*
    | ``withdraw_coinbase(amount, currency, coinbase_account_id)`` [:meth:`API Documentation <copra.rest.Client.withdraw_coinbase>`]
    | Withdraw funds to a Coinbase account.
    
*
    | ``withdraw_crypto(amount, currency, crypto_address)`` [:meth:`API Documentation <copra.rest.Client.withdraw_crypto>`]
    | Withdraw funds to a crypto address.

Stablecoin Conversions
++++++++++++++++++++++

* 
    | ``stablecoin_conversion(from_currency_id, to_currency_id, amount)`` [:meth:`API Documentation <copra.rest.Client.stablecoin_converstion>`]
    | Convert to and from a stablecoin.

Payment Methods
+++++++++++++++

*
    | ``payment_methods()`` [:meth:`API Documentation <copra.rest.Client.payment_methods>`]
    | Get a list of the payment methods you have on file.

Fees
+++++++++++++++

*
    | ``fees()`` [:meth:`API Documentation <copra.rest.Client.fees>`]
    | Get your current maker & taker fee rates and 30-day trailing volume.

Coinbase Accounts
+++++++++++++++++

*
    | ``coinbase_accounts()`` [:meth:`API Documentation <copra.rest.Client.coinbase_accounts>`]
    | Get a list of your coinbase accounts.

Reports
+++++++

*
    | ``create_report(report_type, start_date, end_date, product_id='', account_id='', report_format='pdf', email='')`` [:meth:`API Documentation <copra.rest.Client.create_report>`]
    | Create a report about your account history.
    
*
    | ``report_status(report_id)`` [:meth:`API Documentation <copra.rest.Client.report_status>`]
    | Get the status of a report.

User Account
++++++++++++

*
    | ``trailing_volume()`` [:meth:`API Documentation <copra.rest.Client.trailing_volume>`]
    | Return your 30-day trailing volume for all products.
