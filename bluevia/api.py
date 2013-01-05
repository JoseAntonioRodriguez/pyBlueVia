# -*- coding: utf-8 -*-

'''

'''

import logging
#import uuid
import urllib
import urlparse

from .base_api import BaseApi
from .exceptions import AuthResponseError


log = logging.getLogger(__name__)


class Api(BaseApi):
    '''
    Api 2.0 API client
    '''

    # API endpoints
    _API_BASE_URL = 'https://live-api.bluevia.com/'
    _SB_API_BASE_URL = 'https://sandbox-api.bluevia.com/'
    _AUTH_BASE_URL = 'https://id.tu.com/'

    PATHS = {
        'access_token': 'oauth2/token'
    }

    # OAuth scopes
    SMS_MT = 'sms.send'
    MMS_MT = 'mms.send'

    def __init__(self, client_id, client_secret, access_token=None, sandbox=False):
        '''
        Constructor
        '''

        base_url = self._SB_API_BASE_URL if sandbox else self._API_BASE_URL
        self.auth_base_url = self._AUTH_BASE_URL

        BaseApi.__init__(self, base_url, client_id, client_secret, access_token=access_token)

        self.sandbox = sandbox
        self.oauth_redirect_uri = self.oauth_state = None

    def get_authorization_uri(self, scope, redirect_uri=None, state=None):
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
