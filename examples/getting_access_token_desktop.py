#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This example shows how to get an access token for desktop/native apps (not web based).
Since a 'redirect uri' is not provided to the authorization server, it shows the
OAuth authorization code at the end of the authorization process.
Then this authorization code is changed by the access token.

"""

import webbrowser

import bluevia


# Get your own Client Id and Client Secret creating a new app at bluevia.com
CLIENT_ID = '634dca1685cd2d1c8c5f2577d7595c2f'
CLIENT_SECRET = 'd03136863ff1a493a1f5c9a9ca8ca42e'


if __name__ == '__main__':
    # Create the API wrapper
    bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)

    # Get the authorization uri where the user will give her permission
    # for the app to send SMS and MMS on her behalf
    uri = bluevia_client.get_authorization_uri([bluevia.SMS_MT, bluevia.MMS_MT])
    # Show a message to the user explaining why a browser is going to be opened
    # and what to do with the authorization server

    # Open a browser to show the authorization page
    webbrowser.open(uri, new=1, autoraise=True)

    # Ask the user to enter the auth code shown at the end of the authorization process
    auth_code = raw_input('Enter the auth code: ')

    # Get an access token which will let the app to send SMS and MMS
    access_token = bluevia_client.get_access_token(auth_code)

    # Store the access token for further usage
