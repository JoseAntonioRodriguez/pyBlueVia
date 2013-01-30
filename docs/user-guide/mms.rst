.. _mms-features:

MMS features
============

**pyBlueVia** allows you to perform the following actions regarding MMS:

* Send an MMS
* Query the delivery status of a sent MMS
* Get incomming MMS

.. seealso:: Full examples of how to `use MMS features 
   <https://github.com/JoseAntonioRodriguez/pyBlueVia/blob/master/examples/using_bluevia_api.py>`_
   and how to `deal with MMS notifications
   <https://github.com/JoseAntonioRodriguez/pyBlueVia/blob/master/examples/using_bluevia_api_notifications.py>`_.


.. _sending-mms:

Sending an MMS
--------------

In order to send an MMS you must call the :meth:`~.bluevia.Api.send_mms` method
with the following parameters:

* ``to``: the receipt phone number.
* ``subject``: the MMS subject.
* ``attachments``: a list of attachments to be sent inside the MMS. Each attachment can be:

  - A string, if the attachment is textual content.
  - A file-like object. 
  - A tuple with two elements:

    + A string with the attachment's *content type*.
    + The attachment's binary content.

::

   mms_id = bluevia_client.send_mms(to='34600000000', subject='Hello world!',
                                    attachments=('Look at this pictures',
                                                 open('picture.gif', 'rb'),
                                                 ('image/gif', 'GIF89a[...]')))

This method returns an id which represents the sending, but it says nothing about whether
the MMS has reached the recipient. **pyBlueVia** offers another method to :ref:`ask for the delivery
status of a sent MMS <query-mms-delivery-status>`.

.. note:: This feature requires an *access token*.


.. _query-mms-delivery-status:

Quering the delivery status of a sent MMS
-----------------------------------------

There are two ways of getting information about the delivery status of a sent MMS:

* **Polling**: You explicitly ask for the delivery status using the ``id`` got when sending the MMS.
* **Notifications**: BlueVia sends to your app a notification with the delivery status information.


Polling
^^^^^^^

You can ask for the delivery status of a sent MMS calling the :meth:`~.bluevia.Api.get_mms_delivery_status`
method passing the ``id`` got when sending the MMS. This method returns a dictionary with the
recipient phone number and the status of the sent MMS::

   >>> delivery_status = bluevia_client.get_mms_delivery_status(sms_id)
   >>> print delivery_status
   {u'status': u'delivered', u'address': u'34600000000'}

.. note:: This feature requires an *access token*.


Notifications
^^^^^^^^^^^^^

If you want to receive MMS delivery status notifications from BlueVia the first step is
telling BlueVia where to send those notifications. This is done at the time of sending
the MMS, passing an additional parameter (``callback_url``) with an URL hosted by your
app where delivery status notifications will be processed::

   callback_url = 'https://mydomain.com:8443/delivery_status'
   mms_id = bluevia_client.send_mms(to='34600000000', subject='Hello world!', callback_url=callback_url,
                                    attachments=('Look at this pictures',
                                                 open('picture.gif', 'rb'),
                                                 ('image/gif', 'GIF89a[...]')))

Then BlueVia will send a notification to that URL. These notifications can be parsed by
**pyBlueVia** using the :meth:`~.bluevia.Api.parse_delivery_status` method, passing the
``Content-Type`` HTTP header value together with the body of the received HTTP request::

   >>> delivery_status = bluevia.Api.parse_delivery_status(content_type, content)
   >>> print delivery_status
   {u'status': u'delivered', u'id': u'97286813874922402286', u'address': u'34600000000'}
 
In this case the returned dictionary also includes an ``id`` field with the same value
returned by :meth:`~.bluevia.Api.send_mms`.


.. _getting-incoming-mms:

Getting incoming MMS
--------------------

Each time someone sends an MMS to a `BlueVia short number`_ using your app keyword as the
first word in the subject (or in the first textual attachment), that MMS is available for
being queried by your app. There are two ways of getting incoming MMS:

* **Polling**: You explicitly ask for the available incoming MMS.
* **Notifications**: BlueVia sends to your app a notification each time an MMS is available.

.. _`BlueVia short number`: http://bluevia.com/en/page/tech.overview.shortcodes


Polling
^^^^^^^

In order to ask BlueVia for incoming MMS for your app, simply call the :meth:`~.bluevia.Api.get_incoming_mms`
method, which returns a list of MMS ids. Then to retrieve each MMS content, you must call
the :meth:`~.bluevia.Api.get_incoming_mms_details` method, passing an MMS id as parameter.
This method returns a dictionary with the following keys:

* ``id``: Unique identifier representing this incoming MMS.
* ``from``: phone number from which the MMS was sent.
* ``obfuscated``: a ``bool`` indicating whether the ``from`` is obfuscated or not
  (see :ref:`warning <warning-obfuscation-mms>` below).
* ``to``: short number to which the MMS was sent.
* ``subject``: MMS subject, including the keyword.
* ``timestamp``: date and time of when the MMS was sent, represented as a Python
  `datetime <http://docs.python.org/2/library/datetime.html#datetime.datetime>`_ object.
* ``attachments``: an array of tuples (one per attachment) containing:

  * the attachment's *content type*.
  * the attachment's binary content.

::

   >>> mms_list = bluevia_client.get_incoming_mms()
   >>> mms = bluevia_client.get_incoming_mms_details(mms_list[0])
   >>> print mms
   {u'obfuscated': False, u'from': u'34600000000', u'attachments': [('text/plain', 'Look at this picture'), ('image/gif', 'GIF89a[...]')], u'timestamp': datetime.datetime(2012, 12, 28, 10, 39, 5, 242000), u'to': u'34217040', u'id': u'2515357468066729', u'subject': u'keyword Photo'}


Note that once BlueVia has returned a set of incoming MMS, they are deleted from the server,
so each call to :meth:`~.bluevia.Api.get_incoming_mms` always returns new MMS (if any).

.. _warning-obfuscation-mms:

.. warning:: Due to privacy reasons, some countries do not allow apps to see the phone number
   from which the MMS has been sent. In those cases BlueVia returns an *obfuscated identity*
   which uniquely (and anonymously) represents the sender, and even can be used as a receipt
   when `sending MMS <sending-mms>`_. The ``obfuscated`` flag in the :meth:`~.bluevia.Api.get_incoming_mms`
   response indicates whether the ``from`` identity is obfuscated or not.


Notifications
^^^^^^^^^^^^^

If you want to receive a notification each time an MMS with your keyword is sent to a
BlueVia short number, the first step is to edit your api-key at http://bluevia.com
to configure the URL where your app will be listening to notifications.

These notifications can be parsed by **pyBlueVia** to extract the incoming MMS information
using the :meth:`~.bluevia.Api.parse_incoming_mms` method, passing the ``Content-Type``
HTTP header value together with the body of the received HTTP request::

   >>> mms = bluevia.Api.parse_incoming_mms(content_type, content)
   >>> print mms
   {u'obfuscated': False, u'from': u'34600000000', u'attachments': [('text/plain', 'Look at this picture'), ('image/gif', 'GIF89a[...]')], u'timestamp': datetime.datetime(2012, 12, 28, 10, 39, 5, 242000), u'to': u'34217040', u'id': u'2515357468066729', u'subject': u'keyword Photo'}
 
The returned dictionary is exactly the same returned by :meth:`~.bluevia.Api.get_incoming_mms_details`.

