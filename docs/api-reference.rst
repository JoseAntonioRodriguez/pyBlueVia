.. _api-reference:

API Reference
=============

.. module:: bluevia

Find here the detailed description of **pyBlueVia** classes, methods and exceptions.

.. _`api-reference-summary`:

Summary
-------

.. autosummary::
   
   Api
   Api.client_id
   Api.client_secret
   Api.access_token
   Api.get_authorization_uri
   Api.parse_authorization_response
   Api.get_access_token
   Api.send_sms
   Api.get_sms_delivery_status
   Api.parse_delivery_status
   Api.get_incoming_sms
   Api.parse_incoming_sms
   Api.send_mms
   Api.get_mms_delivery_status
   Api.get_incoming_mms
   Api.get_incoming_mms_details
   Api.parse_incoming_mms


.. _`api-class`:

Api class
---------

.. autoclass:: Api(client_id, client_secret[, access_token, sandbox=False])

   .. autoattribute:: client_id
   .. autoattribute:: client_secret
   .. autoattribute:: access_token
   .. automethod:: get_authorization_uri(scope[, redirect_uri[, state]])
   .. automethod:: parse_authorization_response(uri[, state_to_check])
   .. automethod:: get_access_token(authorization_code[, redirect_uri])
   .. automethod:: send_sms(to, message[, callback_url])
   .. automethod:: get_sms_delivery_status
   .. automethod:: parse_delivery_status
   .. automethod:: get_incoming_sms
   .. automethod:: parse_incoming_sms
   .. automethod:: send_mms(to, subject, attachments[, callback_url])
   .. automethod:: get_mms_delivery_status
   .. automethod:: get_incoming_mms
   .. automethod:: get_incoming_mms_details
   .. automethod:: parse_incoming_mms


.. _`exceptions`:

Exceptions
----------

.. autoexception:: BVException

.. autoexception:: APIError()
   :members:
   :member-order: bysource

.. autoexception:: ContentTypeError

.. autoexception:: AccessTokenError

.. autoexception:: AuthResponseError
