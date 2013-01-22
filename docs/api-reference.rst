.. _api-reference:

API Reference
=============

.. module:: bluevia

Find here the detailed description of every class, method and parameter
of the pyBlueVia API.

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
   .. automethod:: get_received_sms
   .. automethod:: parse_received_sms
   .. automethod:: send_mms(to, subject, attachments[, callback_url])
   .. automethod:: get_mms_delivery_status
   .. automethod:: get_received_mms
   .. automethod:: get_received_mms_details
   .. automethod:: parse_received_mms


Exceptions
----------
 

