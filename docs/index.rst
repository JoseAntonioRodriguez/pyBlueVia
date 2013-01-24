.. pyBlueVia documentation master file, created by
   sphinx-quickstart on Fri Jan 18 11:29:03 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyBlueVia: A Python wrapper around the `BlueVia <http://bluevia.com>`_ API
==========================================================================

Release v\ |version|.

pyBlueVia is an :ref:`MIT Licensed <MIT>` library, written in Python, for making easier the usage of
`BlueVia <http://bluevia.com>`_ API.

pyBlueVia implements an :class:`~.bluevia.Api` class which wraps the BlueVia API, offering methods for:

* Managing OAuth 2.0 authorization process for APIs which need an *access token*.
* Sending SMS and MMS.
* Asking for the delivery status of sent SMS/MMS.
* Retrieve SMS/MMS sent to your app.
* Parsing notifications (delivery status and incoming SMS/MMS) coming from BlueVia.


Introduction
------------

.. toctree::
   :maxdepth: 2
   
   introduction


User guide
----------

.. toctree::
   :maxdepth: 2


API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   
   api-reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. * :ref:`modindex`
