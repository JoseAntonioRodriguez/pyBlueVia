.. _getting-access-token:

Getting an access token
=======================

In order to call some BlueVia features that requires users' authorization your app need
an `OAuth 2.0`_ *access_token*. The procedure to get a BlueVia *access token* is the usual
OAuth dance:

1. The user is redirected to the Authorization Server web site, where she logs in, sees your
   app' details, and gives her permission for your app to call BlueVia on her behalf.
2. After finishing the authorization process, the Authorization Server redirect the user to
   the so-called *redirect uri* (hosted by your app) where you receives an *auth code*.
3. The last step is to exchange the *auth code* by the *access token* which represent the
   user's grant to access BlueVia on her behalf.

The above is the so-called "web flow" because is specially thought for web based apps, where
redirections make sense. If you are making a non-web based app (desktop or native app), the
second step can be modified so that the Authorization Server does not make the redirection
but shows the *auth code* on the screen. In this case your app has to ask the user to enter
that code. Let's call this flow the "desktop flow".

.. _`OAuth 2.0`: http://tools.ietf.org/html/rfc6749


Web flow
--------

The first step is to redirect the user to the Authorization Server. pyBlueVia helps you
to build the Authorization Server's URL by using the :meth:`~.bluevia.Api.get_authorization_uri`
method with the following parameters:

* ``scope``: pyBlueVia support two scopes, which represent the BlueVia features to be authorized:

  - ``bluevia.SMS_MT``: ask for authorization to send SMS and query its delivery status.
  - ``bluevia.MMS_MT``: ask for authorization to send MMS and query its delivery status.

* ``redirect_uri``: URL hosted by your app where the Authorization Server will redirect the
  user after completing the authorization process.
* ``state``: an optional app-dependant string that will be included as a query parameter in
  the *redirect uri* sent to your app. It can be used to correlate both steps.

::

   redirect_uri = 'https://mydomain.com:8443/authorization_response'
   oauth_state = str(uuid.uuid4())
   uri = bluevia_client.get_authorization_uri([bluevia.SMS_MT, bluevia.MMS_MT], redirect_uri, oauth_state)
   # Redirect to the returned uri


Once the user has been redirected to the *redirect uri* hosted by your app, pyBlueVia can
help you to parse the query parameters, using the :meth:`~.bluevia.Api.parse_authorization_response`
method.

This method returns the *auth code* along with the *state* (if it was included in the first step)::

   # 'uri' contains the request uri received by your app as redirected from the Authorization Server
   uri = 'https://mydomain.com/authorization_response?code=TANf0C&state=3829167f-7f5e-42b7-944d-469f9662e738'
   auth_code, state = bluevia.Api.parse_authorization_response(uri)

If this method is called with a *state* value as an input parameter, pyBlueVia will check that
this value matches the one received in the URL, and raise an exception if they don't match::

   try:
      uri = 'https://mydomain.com/authorization_response?code=TANf0C&state=3829167f-7f5e-42b7-944d-469f9662e738'
      auth_code, state = bluevia.Api.parse_authorization_response(uri, '3829167f-7f5e-42b7-944d-469f9662e738')
   except AuthResponseError:
      print 'state parameters do not match.'


The last step consist in exchanging the returned *auth code* for an *access token*. This is
easily done with the :meth:`~.bluevia.Api.get_access_token` method::

   access_token = bluevia_client.get_access_token(auth_code)

After calling this method, the *access token* is also available through the
:attr:`~.bluevia.Api.access_token` attribute. This *access token* represents the user's
authorization to use those BlueVia features covered by the requested *scopes*.

.. seealso:: A full example of how to `get an access token using the web flow 
   <https://github.com/JoseAntonioRodriguez/pyBlueVia/blob/master/examples/getting_access_token_web.py>`_.


Desktop flow
------------

The main difference between the web flow and the desktop flow is that you don't provide a
*callback url* when calling the :meth:`~.bluevia.Api.get_authorization_uri` method:: 

   uri = bluevia_client.get_authorization_uri([bluevia.SMS_MT, bluevia.MMS_MT])

Since this is not a web app, the redirection to the Authorization Server is usually done
by opening a web browser pointing at the returned ``uri``. In this case, the Authorization
Server could not redirect the user to any *uri* when finishing the authorization process,
so the *auth code* will be shown in the browser.

The next step is to ask your user to enter such *code* into your app (by the means you wish).
Then you can call the :meth:`~.bluevia.Api.get_access_token` method to get the *access token*::

   auth_code = raw_input('Enter the auth code: ')
   access_token = bluevia_client.get_access_token(auth_code)

.. seealso:: A full example of how to `get an access token using the desktop flow 
   <https://github.com/JoseAntonioRodriguez/pyBlueVia/blob/master/examples/getting_access_token_desktop.py>`_.

