.. _creating-api-wrapper:

Creating the API wrapper
========================

The first step to use pyBlueVia is to create an :class:`~.bluevia.Api` object, which
represents a BlueVia app, identified by the credentials (*Client id* and *Client secret*)
you got from BlueVia when creating an api-key. Those credentials must be passed
to the :class:`~.bluevia.Api` constructor.

::

   import bluevia
   
   # Get your own Client Id and Client Secret creating a new app at bluevia.com
   CLIENT_ID = '634dca1685cd2d1c8c5f2577d7595c2f'
   CLIENT_SECRET = 'd03136863ff1a493a1f5c9a9ca8ca42e'
   
   bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)

Althouth this is all you need to start making calls to BlueVia, some funcionalities
(such as sending SMS/MMS or quering the delivery status of sent SMS/MMS) need the
user permission because they are done on behalf of the user.

BlueVia uses `OAuth 2.0`_ to manage users' authorization, so an *access token* is required
to to make those calls. To learn how to get BlueVia access tokens see :ref:`getting-access-token`.

In the case that you already have an *access token* (maybe because you got it previously and stored it)
you can pass it as a parameter when creating the :class:`~.bluevia.Api` object::

   ACCESS_TOKEN = '079b8f16c9a159c0d7e2fb0fcfe58d40'
   
   bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)


Or you can set it through the :attr:`~.bluevia.Api.access_token` attribute:: 
 
   bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
   bluevia_client.access_token = ACCESS_TOKEN
   
   
.. _`OAuth 2.0`: http://tools.ietf.org/html/rfc6749
   