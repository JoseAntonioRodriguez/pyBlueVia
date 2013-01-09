#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This example shows how to deal with notifications coming from BlueVia regarding:
  - SMS/MMS delivery status
  - Received SMS/MMS (SMS/MMS sent to a BlueVia shortcode with the keyword chosen during the app creation)

"""

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import ssl
import urlparse

import bluevia


# Get your own Client Id and Client Secret creating a new app at bluevia.com
CLIENT_ID = '634dca1685cd2d1c8c5f2577d7595c2f'
CLIENT_SECRET = 'd03136863ff1a493a1f5c9a9ca8ca42e'
# This is the access token authorized by the user (see getting_access_token_*.py)
ACCESS_TOKEN = '079b8f16c9a159c0d7e2fb0fcfe58d40'


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_parts = urlparse.urlparse(self.path)

        if url_parts.path == '/send_sms':
            # Create the API wrapper
            bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)

            # Send an SMS passing the url where delivery status notifications will be sent
            callback_url = 'https://mydomain.com:8443/delivery_status'
            bluevia_client.send_sms(to='34600000000', message='Hello world!',
                                    callback_url=callback_url)

            self.send_response(200)

    def do_POST(self):
        # BlueVia sends notifications using POST
        url_parts = urlparse.urlparse(self.path)

        content_length = int(self.headers.get('Content-Length'))
        content_type = self.headers.get('Content-Type', None)
        content = self.rfile.read(content_length)

        if url_parts.path == '/delivery_status':
            # Parse the delivery status notification.
            delivery_status = bluevia.Api.parse_delivery_status(content_type, content)

            # Do something with delivery_status

            self.send_response(200)

        elif url_parts.path == '/received_messaging':
            if content_type.startswith('application/'):
                # Parse a notification conveying a received SMS
                sms = bluevia.Api.parse_received_sms(content_type, content)

                # Do something with sms

            elif content_type.startswith('multipart/'):
                # Parse a notification conveying a received MMS
                mms = bluevia.Api.parse_received_mms(content_type, content)

                # Do something with mms

            self.send_response(200)


if __name__ == '__main__':
    # Setup a very simple HTTPS server to receive notifications
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
