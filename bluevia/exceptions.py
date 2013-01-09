# -*- coding: utf-8 -*-

'''

'''


class BVException(Exception):
    pass


class APIError(BVException):
    def __init__(self, resp):
        self.http_status_code = resp.status_code
        self.http_reason = resp.reason  # TODO: Corregir acento: Petici�n incorrecta
        if resp.headers['content-type'] and resp.headers['content-type'].startswith('application/json'):
            content = resp.json()
            if 'exceptionId' in content:
                self.id = content['exceptionId']
                self.message = content['exceptionText']
            elif 'error' in content:
                self.message = content['error']
        else:
            self.message = resp.content

    def __str__(self):
        msg = 'API error: [{0} {1}]'.format(self.http_status_code, self.http_reason)
        if hasattr(self, 'id'):
            msg += ' {0}: {1}'.format(self.id, self.message)
        else:
            msg += ' {0}'.format(self.message)

        return msg


class AccessTokenError(BVException):
    pass


class ContentTypeError(BVException):
    pass


class AuthResponseError(BVException):
    pass
