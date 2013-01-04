# -*- coding: utf-8 -*-

'''

'''


import logging
import json
import re
#import os.path
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
import email
import mimetypes

import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

from .exceptions import APIError, ContentTypeError


log = logging.getLogger(__name__)


PATHS = {
    'access_token': 'oauth2/token',
    'smsoutbound': 'sms/v2/smsoutbound',
    'smsinbound': 'sms/v2/smsinbound',
    'mmsoutbound': 'mms/v2/mmsoutbound',
    'mmsinbound': 'mms/v2/mmsinbound',
    'user_context': 'context/v2/users',
    'location': 'location/v2/location',
    'payment': 'payment/v2/payments'
}


class OAuth2(AuthBase):
    """
    This is a very very simple implementation of OAuth2 to attach an
    OAuth2 bearer token Authorization header to the given Request object.
    """

    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.access_token
        return r


class MakeRequest(object):
    # session is a class attribute so the connection pool is shared among all instances of MakeRequest class
    # and therefore all instances of Api and PartnerApi classes.
    # Note that each MakeRequest instance has its own client_id, client_secret, access token and ssl_client_cert,
    # so each instance deals with a set of credentials, while sharing the connection pool.
    session = requests.Session()
    session.verify = True

    def __init__(self, client_id, client_secret, access_token=None, ssl_client_cert=None):
        self.http_ba = HTTPBasicAuth(client_id, client_secret)
        if access_token:
            self.oauth2 = OAuth2(access_token)
        self.ssl_client_cert = ssl_client_cert

    def __call__(self, url, data=None, attachments=None, url_encoded=False, basic_auth=False):
        '''
        Build the API request and return the formatted result of the API call
        '''

        # Choose the authentication method
        if self.ssl_client_cert:
            auth = self.http_ba
        else:
            auth = self.http_ba if basic_auth else self.oauth2

        # Build the request depending on the input parameters
        if not data:
            # GET
            log.info('GETting from URL: {url}'.format(url=url))
            resp = MakeRequest.session.get(url=url, auth=auth, cert=self.ssl_client_cert)
        elif isinstance(data, dict):
            # POST
            if not attachments:
                # It's not an MMS
                if not url_encoded:
                    # Simple JSON body
                    headers = {'content-type': 'application/json'}
                    data = json.dumps(data, ensure_ascii=False)
                else:
                    # Data passed to Requests as a dictionary is automatically sent as url encoded
                    # and the proper content-type header is automatically set
                    headers = None
            else:
                # Multipart body (MMS)
                body = build_mms_body(data, attachments)
                data = body.as_string().split('\n\n', 1)[1]  # Skipping MIME headers
                # get_content_type() and get_boundary() don't work until as_string() is called
                headers = {'content-type': body.get_content_type() + '; boundary="' + body.get_boundary() + '"'}

            log.info(('POSTting to URL: {url}\n'
                      '  with body: {body}').format(url=url, body=data))
            resp = MakeRequest.session.post(url=url, data=data, headers=headers, auth=auth,
                                            cert=self.ssl_client_cert)
        else:
            raise TypeError("'data' param must be None or a dict")

        log_str = ('Response:\n'
                   '  Status code: {status_code}\n'
                   '  Headers: {headers}\n'
                   '  Body: {body}\n'
                   '  Client id: {client_id}').format(status_code=resp.status_code,
                                                      headers=resp.headers,
                                                      body=resp.content,
                                                      client_id=self.http_ba.username)
        if not basic_auth:
            log_str += '\n  Access token: {access_token}'.format(access_token=self.oauth2.access_token)
        log.info(log_str)

        # Process response
        if resp.status_code in (200, 201):
            if resp.headers['content-length'] == '0':
                return None

            content_type = resp.headers['content-type']
            if not content_type:
                raise ContentTypeError("HTTP response does not contain a Content-Type header")

            if content_type.lower().startswith('application/json'):
                return resp.json()
            elif content_type.lower().startswith('multipart/mixed'):
                root_fields, attachments = parse_mms_body(content_type, resp.content)
                return root_fields, attachments
            else:
                raise ContentTypeError("Unsupported Content-Type '{0}' in HTTP response"
                                       "(only application/json and multipart/mixed are supported".format(content_type))
        elif resp.status_code == 204:
            return None
        else:
            raise APIError(resp)


def build_mms_body(metadata, attachments):
    body = MIMEMultipart(_subtype='mixed')

    # Add MMS metadata (root fields) as a json part
    part = MIMENonMultipart(_maintype='application', _subtype='json')
    part.add_header('Content-Transfer-Encoding', '8bit')
    part.set_payload(payload=json.dumps(metadata, ensure_ascii=False), charset='utf-8')
    del(part['MIME-Version'])
    body.attach(part)

    for attachment in attachments:
        # Textual attachments
        if isinstance(attachment, basestring):
            part = MIMENonMultipart(_maintype='text', _subtype='plain')
            part.add_header('Content-Transfer-Encoding', '8bit')
            part.set_payload(payload=attachment, charset='utf-8')
            del(part['MIME-Version'])
            body.attach(part)

        # Binary attachments (image, audio or video)
        elif isinstance(attachment, (file, tuple, list)):
            if isinstance(attachment, file):
                mimetype = mimetypes.guess_type(attachment.name, strict=False)[0]
                payload = attachment.read()
            else:
                mimetype = attachment[0]
                payload = attachment[1]
            if not mimetype or not '/' in mimetype:
                error_str = "Invalid Content-Type '{0}' in attachment #{1}"
                raise ContentTypeError(error_str.format(mimetype, attachments.index(attachment)))
            maintype, subtype = mimetype.split('/')
            if not maintype in ('image', 'audio', 'video'):
                error_str = ("Unsupported Content-Type '{0}' in attachment #{1} "
                             "(only image, audio or video are supported)")
                raise ContentTypeError(error_str.format(mimetype, attachments.index(attachment)))
            part = MIMENonMultipart(_maintype=maintype, _subtype=subtype)
            part.add_header('Content-Transfer-Encoding', 'binary')
            part.add_header('Content-Disposition', 'attachment')  # , filename=os.path.basename(attachment.name))
            part.set_payload(payload=payload)
            del(part['MIME-Version'])
            body.attach(part)

    return body


def parse_mms_body(content_type, body):
    mime_header = 'Content-Type: ' + content_type + '\n'\
                  'MIME-Version: 1.0\n\n'
    body = email.message_from_string(mime_header + body)

    if not body.is_multipart():
        raise ContentTypeError('Non-multipart body')

    parts = body.get_payload()

    # First part MUST convey MMS metadata (root fields)
    metadata = parts[0]
    content_type = metadata.get_content_type().lower()
    metadata = metadata.get_payload(decode=True)
    if content_type == 'application/json':
        try:
            metadata = json.loads(metadata)
        except ValueError:
            raise ValueError('Bad JSON content in MMS metadata')
    elif content_type == 'application/xml':
        try:
            metadata = xml_to_dict(metadata, ('id', 'from', 'to', 'subject', 'timestamp'))
        except KeyError:
            raise ValueError('Bad XML content in MMS metadata')
    else:
        raise ContentTypeError("Unsupported Content-Type '{0}' in MMS metadata "
                               "(only application/json and application/xml are supported".format(content_type))

    # Go through the rest of parts, which are the MMS attachments
    attachments = [(part.get_content_type(),
                    part.get_payload(decode=True)) for part in parts[1:]]

    return metadata, attachments


def xml_to_dict(xml, keys):
    try:
        if not isinstance(xml, unicode):
            xml = unicode(xml, 'utf-8')

        dict_ = {}
        for key in keys:
            if not isinstance(key, unicode):
                key = unicode(key, 'utf-8')
            dict_[key] = re.search('<.*' + key + '>(.*)</.*' + key + '>', xml).group(1)

        return dict_
    except AttributeError:
        raise KeyError('XML does not contain the key: ' + key)


def sanitize(output):
    # Change dictionary values as follows:
    #   - remove 'tel:+'/'alias:' prefixes from 'to'/'from'/'address' keys' values
    #   - add 'obfuscated' key when 'from' key is present
    #   - convert 'timestamp' keys' values to datetime object

    if isinstance(output, dict):
        for (k, v) in output.items():
            if k in ('from', 'to', 'address'):
                obfuscated = v.startswith('alias:')
                output[k] = v[6:] if obfuscated else v[5:]
                if k == 'from':
                    output[u'obfuscated'] = obfuscated
            elif k == 'timestamp':
                output[k] = datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f+0000')

        return output
    elif isinstance(output, list):
        return [sanitize(item) for item in output]
    else:
        return output
