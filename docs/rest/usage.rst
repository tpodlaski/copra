=====
Usage
=====

.. warning::

  Any references made below to specific aspects of the Coinbase Pro API such as the data structures returned by methods may be out of date. Please visit `Coinbase Pro's WebSocket REST API documentation <https://docs.pro.coinbase.com/#api/>`__ for the authorative and up to date API information.
  
Introduction
------------
:class:`copra.rest.Client`, the asyncronous REST client class provided by CoPrA, is intentionally simple. Its methods were designed specifically to replicate all of the endpoints offered by the Coinbase Pro REST service, both in the parameters they expect and the data they return. 

With very few exceptions there is a one to one correspondence between :class:`copra.rest.Client` methods and the Coinbase endpoints. As often as possible, parameter names were kept the same and the json-encoded lists and dicts returned by the API server are, in turn, returned by the client methods untouched. This makes it simple to cross reference the CoPrA source code and documentation with Coinbase's own documentation (https://docs.pro.coinbase.com/#api/). 

Additionally, it should be relatively easy to extend the client in order to build finer grained ordering methods, sophisticated account management systems, and powerful market analytics tools.

Errors
------
While :class:`copra.rest.Client` takes a hands-off approach to the data returned from API server, it does involve itself while preparing the user-supplied method paramters that will become part of the REST request. Specifically, in instances where the client can identify that the provided parameters will return an error from the API server, it raises a descriptive :class:`ValueError` in order to avoid an unnecessary server call. 

For example, the client method :meth:`copra.rest.Client.market_order` has parameters for the amount of currency to purchase or sell, ``size``, and for the amount of quote currency to use for the transaction, ``funds``. For a market order, it is impossible to require both so if both are sent in the method call, the client raises a :class:`ValueError`.

The :class:`copra.rest.Client` API documentation details for each method in what instances :class:`ValueErrors` are raised.

copra.rest.APIRequestError
++++++++++++++++++++++++++

On the other hand, there will be times the client cannot tell ahead of time that an API request will return error. Insufficient funds, invalid account ids, improper authorization, and internal server errors are just a few examples of the errors a request may return.

Because there are many potential error types, and the Coinbase documentation does not list them all, the :class:`copra.rest.Client` raises a generic error, :class:`copra.rest.APIRequestError`, whenever the HTTP status code of an API server response is non-2xx.

.. autoclass:: copra.rest.APIRequestError
