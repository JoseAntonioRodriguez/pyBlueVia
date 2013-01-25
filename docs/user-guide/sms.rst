.. _sms-features:

SMS features
============

**pyBlueVia** allows you to perform the following actions regarding SMS:

* Send an SMS
* Query the delivery status of a sent SMS
* Get incomming SMS


.. _sending-sms:

Sending an SMS
--------------

Sending an SMS is as easy as calling the :meth:`~.bluevia.Api.send_sms` method passing the
recipient phone number and the text to be sent::

   sms_id = bluevia_client.send_sms(to='34600000000', message='Hello world!')

This method returns an id which represents the sending, but it says nothing about whether
the SMS has reached the recipient. **pyBlueVia** offers another method to :ref:`ask for the delivery
status of a sent SMS <query-sms-delivery-status>`.

.. note:: This feature requires an *access token*.


.. _query-sms-delivery-status:

Quering the delivery status of a sent SMS
-----------------------------------------

There are two ways of getting information about the delivery status of a sent SMS:

* **Polling**: You explicitly ask for the delivery status using the ``id`` got when sending the SMS.
* **Notifications**: BlueVia sends to your app a notification with the delivery status information.


Polling
^^^^^^^

You can ask for the delivery status of a sent SMS calling the :meth:`~.bluevia.Api.get_sms_delivery_status`
method passing the ``id`` got when sending the SMS. This method returns a dictionary with the
recipient phone number and the status of the sent SMS::

   >>> delivery_status = bluevia_client.get_sms_delivery_status(sms_id)
   >>> print delivery_status
   {u'status': u'delivered', u'address': u'34600000000'}

.. note:: This feature requires an *access token*.


Notifications
^^^^^^^^^^^^^

If you want to receive SMS delivery status notifications from BlueVia the first step is
telling BlueVia where to send those notifications. This is done at the time of sending
the SMS, passing an additional parameter (``callback_url``) with an URL hosted by your
app where delivery status notifications will be processed::

   callback_url = 'https://mydomain.com:8443/delivery_status'
   bluevia_client.send_sms(to='34600000000', message='Hello world!', callback_url=callback_url)

Then BlueVia will send a notification to that URL. These notifications can be parsed by
**pyBlueVia** using the :meth:`~.bluevia.Api.parse_delivery_status` method, passing the
``Content-Type`` HTTP header value together with the body of the received HTTP request::

   >>> delivery_status = bluevia.Api.parse_delivery_status(content_type, content)
   >>> print delivery_status
   {u'status': u'delivered', u'id': u'97286813874922402286', u'address': u'34600000000'}
 
In this case the returned dictionary also includes an ``id`` field with the same value
returned by :meth:`~.bluevia.Api.send_sms`.


Getting incoming SMS
--------------------

Each time someone sends an SMS to a `BlueVia short number`_ using your app keyword as the
first word in the text, that SMS is available for being queried by your app.
There are two ways of getting incoming SMS:

* **Polling**: You explicitly ask for the available incoming SMS.
* **Notifications**: BlueVia sends to your app a notification each time an SMS is available.

.. _`BlueVia short number`: http://bluevia.com/en/page/tech.overview.shortcodes


Polling
^^^^^^^

In order to ask BlueVia for incoming SMS for your app, simply call the :meth:`~.bluevia.Api.get_incoming_sms`
method. It returns a list of dictionaries (one per SMS) with the following SMS data:

* ``id``: Unique identifier representing this incoming SMS.
* ``from``: phone number from which the SMS was sent.
* ``obfuscated``: a ``bool`` indicating whether the ``from`` is obfuscated or not
  (see :ref:`warning <warning-obfuscation-sms>` below).
* ``to``: short number to which the SMS was sent.
* ``message``: SMS text, including the keyword.
* ``timestamp``: date and time of when the SMS was sent, represented as a Python
  `datetime <http://docs.python.org/2/library/datetime.html#datetime.datetime>`_ object.

::

   >>> sms = bluevia_client.get_incoming_sms()
   >>> print sms
   {u'obfuscated': False, u'from': u'34600000000', u'timestamp': datetime.datetime(2012, 12, 27, 16, 17, 42, 418000), u'to': u'34217040', u'message': u'keyword Hello world!', u'id': u'97286813874922402286'}

Note that once BlueVia has returned a set of incoming SMS, they are deleted from the server,
so each call to :meth:`~.bluevia.Api.get_incoming_sms` always returns new SMS (if any).

.. _warning-obfuscation-sms:

.. warning:: Due to privacy reasons, some countries do not allow apps to see the phone number
   from which the SMS has been sent. In those cases BlueVia returns an *obfuscated identity*
   which uniquely (and anonymously) represents the sender, and even can be used as a receipt
   when `sending SMS <sending-sms>`_. The ``obfuscated`` flag in the :meth:`~.bluevia.Api.get_incoming_sms`
   response indicates whether the ``from`` identity is obfuscated or not.


Notifications
^^^^^^^^^^^^^

If you want to receive a notification each time an SMS with your keyword is sent to a
BlueVia short number, the first step is to edit your api-key at http://bluevia.com
to configure the URL where your app will be listening to notifications.

These notifications can be parsed by **pyBlueVia** to extract the incoming SMS information
using the :meth:`~.bluevia.Api.parse_incoming_sms` method, passing the ``Content-Type``
HTTP header value together with the body of the received HTTP request::

   >>> sms = bluevia.Api.parse_incoming_sms(content_type, content)
   >>> print sms
   {u'obfuscated': False, u'from': u'34600000000', u'timestamp': datetime.datetime(2012, 12, 27, 16, 17, 42, 418000), u'to': u'34217040', u'message': u'keyword Hello world!', u'id': u'97286813874922402286'}
 
The returned dictionary is exactly the same that each element of the list returned by
:meth:`~.bluevia.Api.get_incoming_sms`.

