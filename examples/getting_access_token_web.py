#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This example shows how to get an access token for web apps.
Since the authorization server is provided with a 'redirect uri', it will redirect
the browser to that uri at the end of the authorization process, including the
OAuth authorization code as a query parameter.
Then this authorization code is changed by the access token.

"""

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import ssl
import urlparse
import uuid

import bluevia


# Get your own Client Id and Client Secret creating a new app at bluevia.com
CLIENT_ID = '634dca1685cd2d1c8c5f2577d7595c2f'
CLIENT_SECRET = 'd03136863ff1a493a1f5c9a9ca8ca42e'


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    # Create the API wrapper as a class attribute
    # Note that this is a simple example and it is not thread safe
    bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)

    def do_GET(self):
        url_parts = urlparse.urlparse(self.path)

        if url_parts.path == '/':
            # Get the authorization uri where the user will give her permission
            # for the app to send SMS and MMS on her behalf
            #   - redirect_uri is the uri where the app expects to receive the authorization response
            #   - oauth_state is a correlator to match the request with the response
            redirect_uri = 'https://mydomain.com:8443/authorization_response'
            oauth_state = str(uuid.uuid4())
            uri = MyHTTPRequestHandler.bluevia_client.get_authorization_uri([bluevia.SMS_MT, bluevia.MMS_MT],
                                                                            redirect_uri, oauth_state)
            # Show a message to the user explaining why she is going to be redirected
            # to the authorization server and what to do there.

            # Redirect to the authorization uri
            self.send_response(301)
            self.send_header('Location', uri)
            self.end_headers()

        elif url_parts.path == '/authorization_response':
            # Parse the authorization response to get the authorization code.
            auth_code = MyHTTPRequestHandler.bluevia_client.parse_authorization_response(self.path)

            # Get an access token which will let the app to send SMS and MMS.
            access_token = MyHTTPRequestHandler.bluevia_client.get_access_token(auth_code)

            # Store the access token for further usage

            self.send_response(200)


if __name__ == '__main__':
    # Setup a very simple HTTPS server to receive authorization results
    try:
        server_address = ('', 8443)
        httpd = HTTPServer(server_address, MyHTTPRequestHandler)
        httpd.socket = ssl.wrap_socket(httpd.socket,
                                       certfile='cert.pem', keyfile='private_key.pem',
                                       server_side=True)
        print 'Server started...'
        httpd.serve_forever()

    except KeyboardInterrupt:
        print '\n^C received, shutting down server...'
        httpd.socket.close()
