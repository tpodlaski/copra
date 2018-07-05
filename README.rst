=========================================
Coinbase Pro Asyncronous Websocket Client
=========================================


.. image:: https://img.shields.io/pypi/v/copra.svg
        :target: https://pypi.python.org/pypi/copra

.. image:: https://img.shields.io/travis/tpodlaski/copra.svg
        :target: https://travis-ci.org/tpodlaski/copra

.. image:: https://readthedocs.org/projects/copra/badge/?version=latest
        :target: https://copra.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
        


copra \(**co**\ inbase **pr**\ o **a**\ sync\) is an asyncronous websocket client written in Python for use with the Coinbase Pro virtual currency trading platform. To learn about Coinbase Pro's websocket service including the available channels and the data they provide, please see Coinbase Pro's API documentation at: https://docs.pro.coinbase.com/#websocket-feed.


Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.4 or greater
* Autobahn|Python

The base websocket functionality for copra is provided by **Autobahn|Python**, the open-source (MIT) real-time framework for web, mobile & the Internet of Things.

If you install copra using pip, Autobahn will be installed automatically. To install Autobahn manually using pip::

    $ pip3 install autobahn

Autobahn can also be installed from source by downnloading the code from: https://github.com/crossbario/autobahn-python .


Installing
~~~~~~~~~~

The easiest way to install copra (and its dependencies) is by using pip::

    $ pip3 install copra

copra can also be installed from source:


Examples
~~~~~~~~

You will likely want to override ``copra.websocket.client``, but it can be used 'as is' to test the module through the command line::

    #example.py

    import asyncio
    import logging
    
    from copra.websocket import Channel, Client
    
    
    loop = asyncio.get_event_loop()

    ws = Client(loop, [Channel('heartbeat', 'BTC-USD')])
    ws.add_as_task_to_loop()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(ws.close())
        loop.close()
  
  

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


.. _SemVer: http://semver.org/
.. _`tags on this repository`: https://github.com/tpodlaski/copra/tags
.. _`LICENSE`: https://github.com/tpodlaski/copra/blob/master/LICENSE
.. _contributers: https://github.com/tpodlaski/copra/blob/master/CONTRIBUTING.rst
.. _`CONTRIBUTING.rst`: https://github.com/tpodlaski/copra/blob/master/CONTRIBUTING.rst
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
