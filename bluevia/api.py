# -*- coding: utf-8 -*-

"""
bluevia.api
~~~~~~~~~~~

This module implements the pyBlueVia API class.

:copyright: (c) 2013 by Jose Antonio Rodríguez.
:license: MIT, see LICENSE for more details.

"""

import logging
#import uuid
import urllib
import urlparse

from .base_api import BaseApi
from .exceptions import AuthResponseError


log = logging.getLogger(__name__)


# OAuth scopes
SMS_MT = 'sms.send'
MMS_MT = 'mms.send'


class Api(BaseApi):

    """This is the main pyBlueVia class, which wraps the BlueVia API.

    The first step to use pyBlueVia is to create an :class:`Api <Api>` object.

    :param client_id: OAuth 2.0 *client id*.
    :param client_secret: OAuth 2.0 *client secret*.
    :param access_token: (optional) OAuth 2.0 *access token* needed to send sms and mms or to get their delivery
        status. If not provided here it can be set later setting the attribute :attr:`access_token` or during
        the OAuth authorization process when calling :meth:`get_access_token`.
    :param sandbox: (optional) set to ``True`` in order to use the BlueVia Sandbox feature. Default is ``False``.
    :type sandbox: bool

    Usage::

        >>> import bluevia
        >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)
        >>> bluevia_client.send_sms(to='34600000000', message='Hello world!')

    """

    # API endpoints
    _API_BASE_URL = 'https://live-api.bluevia.com/'
    _SB_API_BASE_URL = 'https://sandbox-api.bluevia.com/'
    _AUTH_BASE_URL = 'https://id.tu.com/'

    PATHS = {
        'access_token': 'oauth2/token'
    }

    def __init__(self, client_id, client_secret, access_token=None, sandbox=False):
        base_url = self._SB_API_BASE_URL if sandbox else self._API_BASE_URL
        self.auth_base_url = self._AUTH_BASE_URL

        BaseApi.__init__(self, base_url, client_id, client_secret, access_token=access_token)

        self.sandbox = sandbox
        self.oauth_redirect_uri = self.oauth_state = None

    def get_authorization_uri(self, scope, redirect_uri=None, state=None):

        """Build the OAuth authorization URI.

        As a first step to get an access token (needed to call some of the BlueVia APIs) the user must
        be redirected to the Authorization Server, where she will authorize your app to make such calls
        on her behalf.
        The URI where the user must be redirected is built by this method based on the input parameters.

        :param scope: *scope* (or array/tuple of scopes) for which the authorization is requested.
            Supported *scope* values are: ``bluevia.SMS_MT`` and ``bluevia.MMS_MT`` which ask for permission
            to send SMS and MMS, respectively (and ask for the delivery status).
        :param redirect_uri: (optional) following the OAuth dance, after completing the authorization, the
            user will be redirected to this URI (hosted by your app) including query parameters that could
            be parsed by :meth:`parse_authorization_response` as a previous step to get the *access token*.
            If this parameter is not provided, the Authorization Server will show an *authorization code* that
            the user must provide to your app to continue with the process of getting the *access token*.
        :param state: (optional) if provided, the Authorization Server will include it in the *redirect uri*
            and will be returned by :meth:`parse_authorization_response`. It may be used to correlate
            authorization requests with their responses.
        :returns: The authorization URI.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> uri = bluevia_client.get_authorization_uri([bluevia.SMS_MT, bluevia.MMS_MT], 'https://mydomain.com/authorization_response', '3829167f-7f5e-42b7-944d-469f9662e738')
            >>> print uri
            https://id.tu.com/authorize?scope=sms.send+mms.send&state=3829167f-7f5e-42b7-944d-469f9662e738&redirect_uri=https%3A%2F%2Fmydomain.com%2Fauthorization_response&response_type=code&client_id=634dca1685cd2d1c8c5f2577d7595c2f

        .. seealso:: OAuth 2.0 specification: `Authorization Request <http://tools.ietf.org/html/rfc6749#section-4.1.1>`_.

        """

        if isinstance(scope, str):
            scope = [scope]
        scope = ' '.join(scope)

#        if redirect_uri and not state:
#            state = str(uuid.uuid4())

        params = {'client_id': self.client_id,
                  'scope': scope,
                  'response_type': 'code'}

        if redirect_uri:
            self.oauth_redirect_uri = redirect_uri
            params['redirect_uri'] = redirect_uri
        if state:
            self.oauth_state = state
            params['state'] = state

        uri = self.auth_base_url + 'authorize?' + urllib.urlencode(params)
        log.info('Authorization URI: ' + uri)

        return uri

    def parse_authorization_response(self, uri, state_to_check=None):

        """Parse the OAuth authorization response and returns the *Authorization Code* and *State*.

        If a *redirect uri* parameter was provided to :meth:`get_authorization_uri`, the Authorization Server
        redirect the user to that URI including the result of the authorization process as query parameters.
        This method will parse that URI and returns the *authorization code* needed to get the access token and
        the *state* provided to :meth:`get_authorization_uri`,
        if any.

        :param uri: the URI where the Authorization Server redirected the user after the authorization process.
        :param state_to_check: (optional) if provided, this value will be checked against the value included in
            the parsed URI. If they don't match a :exc:`AuthResponseError` exception will be raised.
        :returns: The *authorization code* to be used to call :meth:`get_access_token`, or a tuple containing the
            *authorization code* and the *state* if it was included in the parsed URI.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> uri = 'https://mydomain.com/authorization_response?code=TANf0C&state=3829167f-7f5e-42b7-944d-469f9662e738'
            >>> auth_code, state = bluevia_client.parse_authorization_response(uri)
            >>> print auth_code
            TANf0C

        .. seealso:: OAuth 2.0 specification: `Authorization Response <http://tools.ietf.org/html/rfc6749#section-4.1.2>`_.

        """

        state_to_check = state_to_check or self.oauth_state

        url_parts = urlparse.urlparse(uri)
        query_params = urlparse.parse_qs(url_parts.query, keep_blank_values=True, strict_parsing=False)

        if 'code' in query_params:
            code = query_params['code']
            if len(code) > 1:
                raise AuthResponseError("More than one value for 'code' parameter")
            else:
                code = code[0]

            if state_to_check:
                if 'state' in query_params:
                    state = query_params['state']
                    if len(state) > 1:
                        raise AuthResponseError("More than one value for 'state' parameter")
                    else:
                        state = state[0]
                else:
                    raise AuthResponseError("'state' parameter not found")

                if state_to_check != state:
                    raise AuthResponseError("'state' parameters do not match")

            return code

        elif 'error' in query_params:
            error = query_params['error'][0]
            if 'error_description' in query_params:
                error += ' (' + query_params['error_description'][0] + ')'

            raise AuthResponseError('Authorization Server error: {0}'.format(error))

        else:
            raise AuthResponseError('Authorization Server response does not conform to OAuth 2.0')

    def get_access_token(self, authorization_code, redirect_uri=None):

        """Exchange the given *authorization code* for an *access token*.

        :param authorization_code: the *authorization code* returned by :meth:`parse_authorization_response` or
            provided to your app by other means (for those apps not providing a *redirect uri* parameter to
            :meth:`get_authorization_uri`).
        :param redirect_uri: (optional) if provided, it must be the same passed to :meth:`get_authorization_uri`.
            If not provided pyBlueVia remembers the one passed to :meth:`get_authorization_uri`, if any.
        :returns: The *access token* to be used to call BlueVia APIs, valid for the requested *scopes*. The returned
            access token is also stored in the :attr:`access_token` attribute.

        Usage::

            >>> import bluevia
            >>> bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET)
            >>> access_token = bluevia_client.get_access_token('TANf0C')
            >>> print access_token
            079b8f16c9a159c0d7e2fb0fcfe58d40

        .. seealso:: OAuth 2.0 specification: `Access Token Request <http://tools.ietf.org/html/rfc6749#section-4.1.3>`_
               and `Access Token Response <http://tools.ietf.org/html/rfc6749#section-4.1.4>`_.

        """

        redirect_uri = redirect_uri or self.oauth_redirect_uri

        url = self.base_url + self.PATHS['access_token']

        data = {'grant_type': 'authorization_code',
                'code': authorization_code}

        if redirect_uri:
            data['redirect_uri'] = redirect_uri

        resp = self._make_request(url, data, url_encoded=True, basic_auth=True)

        access_token = resp['access_token']
        self.access_token = access_token  # Calls property on BaseApi class

        return access_token

    def send_sms(self, to, message, callback_url=None):
        return BaseApi.send_sms(self, from_=None, to=to, message=message, callback_url=callback_url)

    def get_sms_delivery_status(self, sms_id):
        return BaseApi.get_sms_delivery_status(self, sms_id=sms_id)

    def get_received_sms(self):
        return BaseApi.get_received_sms(self)

    def send_mms(self, to, subject, attachments, callback_url=None):
        return BaseApi.send_mms(self, from_=None, to=to, subject=subject,
                                attachments=attachments, callback_url=callback_url)

    def get_mms_delivery_status(self, mms_id):
        return BaseApi.get_mms_delivery_status(self, mms_id=mms_id)

    def get_received_mms(self):
        return BaseApi.get_received_mms(self)

    def get_received_mms_details(self, mms_id):
        return BaseApi.get_received_mms_details(self, mms_id=mms_id)
