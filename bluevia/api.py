# -*- coding: utf-8 -*-

'''

'''

import logging
import json
#import uuid
import urllib
import urlparse

from .utils import PATHS, MakeRequest, parse_mms_body, xml_to_dict, sanitize
from .exceptions import ContentTypeError, AuthResponseError


log = logging.getLogger(__name__)


class Api(object):
    '''
    Api 2.0 API client
    '''

    # API endpoints
    _API_BASE_URL = 'https://live-api.bluevia.com/'
    _SB_API_BASE_URL = 'https://sandbox-api.bluevia.com/'
    _AUTH_BASE_URL = 'https://id.tu.com/'

    # OAuth scopes
    SMS_MT = 'sms.send'
    MMS_MT = 'mms.send'

    def __init__(self, client_id, client_secret, access_token=None, sandbox=False):
        '''
        Constructor
        '''

        self._make_request = MakeRequest(client_id, client_secret, access_token)
        self.sandbox = sandbox
        if sandbox:
            self.base_url = self._SB_API_BASE_URL
        else:
            self.base_url = self._API_BASE_URL
        self.auth_base_url = self._AUTH_BASE_URL

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

        url = self.base_url + PATHS['access_token']

        data = {'grant_type': 'authorization_code',
                'code': authorization_code}

        if redirect_uri:
            data['redirect_uri'] = redirect_uri

        resp = self._make_request(url, data, url_encoded=True, basic_auth=True)

        return resp['access_token']

    def send_sms(self, to, message, callback_url=None):
        url = self.base_url + PATHS['smsoutbound']

        # If 'to' contains only digits, it's an MSISDN, else it's an obfuscated identity
        data = {'to': 'tel:+' + to if to.isdigit() else 'alias:' + to,
                'message': message}

        if callback_url:
            data['callbackUrl'] = callback_url

        resp = self._make_request(url, data)

        return resp['id']

    def get_sms_delivery_status(self, sms_id):
        if sms_id.startswith('http://') or sms_id.startswith('https://'):
            url = sms_id + '?fields=to'
        else:
            url = self.base_url + PATHS['smsoutbound'] + '/' + sms_id + '?fields=to'

        resp = self._make_request(url)

        return sanitize(resp['to'])
#        return [{u'to': to['address'][6:] if to['address'].startswith('alias:') else to['address'][5:],
#                 u'status': to['status']} for to in resp['to']]

    @staticmethod
    def parse_delivery_status(content_type, content):
        if content_type.startswith('application/json'):
            try:
                delivery_status = json.loads(content)
            except ValueError:
                raise ValueError('Bad JSON content')

            return sanitize(delivery_status)
#            delivery_status[u'address'] = delivery_status['address'][6:]\
#                                          if delivery_status['address'].startswith('alias:')\
#                                          else delivery_status['address'][5:]
#            return delivery_status
        else:
            raise ContentTypeError("Unsupported Content-Type '{0}' "
                                   "(only application/json is supported".format(content_type))

    def get_received_sms(self):
        url = self.base_url + PATHS['smsinbound']

        resp = self._make_request(url, basic_auth=True)

        if resp:
            return sanitize(resp)
#            return [{u'id': sms['id'],
#                     u'from': sms['from'][6:] if sms['from'].startswith('alias:') else sms['from'][5:],
#                     u'obfuscated': sms['from'].startswith('alias:'),
#                     u'to': sms['to'][5:],
#                     u'message': sms['message'],
#                     u'timestamp': datetime.strptime(sms['timestamp'], '%Y-%m-%dT%H:%M:%S.%f+0000')} for sms in resp]
        else:
            return []

    @staticmethod
    def parse_received_sms(content_type, content):
        if content_type.startswith('application/json'):
            try:
                sms = json.loads(content)
            except ValueError:
                raise ValueError('Bad JSON content')
        elif content_type.startswith('application/xml'):
            try:
                sms = xml_to_dict(content, ('id', 'from', 'to', 'message', 'timestamp'))
            except KeyError:
                raise ValueError('Bad XML content')
        else:
            raise ContentTypeError("Unsupported Content-Type '{0}' "
                                   "(only application/json and application/xml are supported".format(content_type))

        return sanitize(sms)
#        sms[u'obfuscated'] = sms['from'].startswith('alias:')
#        sms[u'from'] = sms['from'][6:] if sms['obfuscated'] else sms['from'][5:]
#        sms[u'to'] = sms['to'][5:]
#        sms[u'timestamp'] = datetime.strptime(sms['timestamp'], '%Y-%m-%dT%H:%M:%S.%f+0000')
#        return sms

    def send_mms(self, to, subject, attachments, callback_url=None):
        # TODO: Test MMS w/o attachments
        url = self.base_url + PATHS['mmsoutbound']

        # If 'to' contains only digits, it's an MSISDN, else it's an obfuscated identity
        metadata = {'to': 'tel:+' + to if to.isdigit() else 'alias:' + to,
                    'subject': subject}

        if callback_url:
            metadata['callbackUrl'] = callback_url

        resp = self._make_request(url, metadata, attachments)

        return resp['id']

    def get_mms_delivery_status(self, mms_id):
        if mms_id.startswith('http://') or mms_id.startswith('https://'):
            url = mms_id + '?fields=to'
        else:
            url = self.base_url + PATHS['mmsoutbound'] + '/' + mms_id + '?fields=to'

        resp = self._make_request(url)

        return sanitize(resp['to'])
#        return [{u'to': to['address'][6:] if to['address'].startswith('alias:') else to['address'][5:],
#                 u'status': to['status']} for to in resp['to']]

    def get_received_mms(self):
        url = self.base_url + PATHS['mmsinbound']

        resp = self._make_request(url, basic_auth=True)

        if resp:
            return [mms['id'] for mms in resp]
        else:
            return []

    def get_received_mms_details(self, mms_id):
        # TODO: Test MMS w/o attachments
        url = self.base_url + PATHS['mmsinbound'] + '/' + mms_id

        metadata, attachments = self._make_request(url, basic_auth=True)

        mms = sanitize(metadata)
        mms[u'attachments'] = attachments
        return mms
#        return {u'id': metadata['id'],
#                u'from': metadata['from'][6:] if metadata['from'].startswith('alias:')
#                         else metadata['from'][5:],
#                u'obfuscated': metadata['from'].startswith('alias:'),
#                u'to': metadata['to'][5:],
#                u'subject': metadata['subject'],
#                u'timestamp': datetime.strptime(metadata['timestamp'], '%Y-%m-%dT%H:%M:%S.%f+0000'),
#                u'attachments': attachments}

    @staticmethod
    def parse_received_mms(content_type, content):
        metadata, attachments = parse_mms_body(content_type, content)

        mms = sanitize(metadata)
        mms[u'attachments'] = attachments
        return mms
#        return {u'id': metadata['id'],
#                u'from': metadata['from'][6:] if metadata['from'].startswith('alias:')
#                         else metadata['from'][5:],
#                u'obfuscated': metadata['from'].startswith('alias:'),
#                u'to': metadata['to'][5:],
#                u'subject': metadata['subject'],
#                u'timestamp': datetime.strptime(metadata['timestamp'], '%Y-%m-%dT%H:%M:%S.%f+0000'),
#                u'attachments': attachments}
