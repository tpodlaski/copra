=====
Usage
=====

.. warning::

  Any references made below to specific aspects of the Coinbase Pro API such as the data returned by methods may be out of date. Please visit `Coinbase Pro's WebSocket REST API documentation <https://docs.pro.coinbase.com/#api/>`__ for the authorative and up to date API information.
  
Introduction
------------
``copra.rest.Client``, the asyncronous REST client class provided by CoPrA, is intentionally simple. Its methods were designed specifically to replicate all of the endpoints offered by the Coinbase Pro REST service, both in the parameters they expect and the data they return. 

With very few exceptions there is a one to one correspondence between ``copra.rest.Client`` methods and the Coinbase endpoints. As often as possible, parameter names were kept the same and the json-encoded lists and dicts returned by the API server are, in turn, returned by the client methods untouched. This makes it simple to cross reference the CoPrA source code and documentation with Coinbase's own documentation (https://docs.pro.coinbase.com/#api/). 

Additionally, it should be relatively easy to extend the client in order to build finer grained ordering methods, sophisticated account management systems, and powerful market analytics tools.

