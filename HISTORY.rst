=======
History
=======

0.1.0 (2018-07-06)
------------------

* First release on PyPI.

0.2.0 (2018-07-07)
------------------

* Added Client authentication.

0.3.0 (2018-07-09)
------------------

* Added reconnect option to Client.

0.4.0 (2018-07-10)
------------------
* Added subscribe and unsubscribe methods to Client.

1.0.0 (2018-07-12)
------------------
* Added full documentation of the CoPrA API.

1.0.1 (2018-07-12)
------------------
* Fixed typos in the documentation.

1.0.2 (2018-07-12)
------------------
* Added Examples page to the documentation.

1.0.3 (2018-07-16)
------------------
* More documentation typos fixed.

1.0.4 - 1.0.5 (2018-07-17)
--------------------------
* Non-API changes.

1.0.6 (2018-08-19)
------------------
* Updated Autobahn requirement to 18.8.1

1.0.7 (2018-08-19)
------------------
* Modified Travis config to test against Python 3.7.

1.1.0 (2018-11-27)
------------------
* Added REST client.

1.1.2 (2018-12-01)
------------------
* Updated documentation formatting.

1.2.0 (2019-01-04)
------------------
* Created copra.rest package and moved old copra.rest module to
  copra.rest.client.
* Created copra.websocket package and moved old copra.websocket module to
  copra.websocket.client.
* Add imports to copra.rest.__init__ and copra.websocket.__init__ so that
  classes and attributes can still be imported as they were before.
* Rewrote and completed unit tests from copra.websocket.

1.2.5 (2019-01-05)
------------------
* Updated copra.websocket.client unit tests to ignore those that are 
  incompatible with Python 3.5 due to Mock methods that were not yet 
  implemented.
  
1.2.6 (2019-01-07)
------------------
* Updated the REST client to attach an additional query string parameter 
  to all GET requests. The parameter, 'no-cache', is a timestamp and ensures
  that the Coinbase server responds to all GET requests with fresh and not
  cached content.