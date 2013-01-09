#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This example shows how to use the BlueVia API to:
  - Send SMS/MMS
  - Ask for the delivery status of a sent SMS/MMS
  - Get received SMS/MMS (SMS/MMS sent to a BlueVia shortcode with the keyword chosen during the app creation)

"""

import mimetypes

import bluevia


# Get your own Client Id and Client Secret creating a new app at bluevia.com
CLIENT_ID = '634dca1685cd2d1c8c5f2577d7595c2f'
CLIENT_SECRET = 'd03136863ff1a493a1f5c9a9ca8ca42e'
# This is the access token authorized by the user (see getting_access_token_*.py)
ACCESS_TOKEN = '079b8f16c9a159c0d7e2fb0fcfe58d40'


if __name__ == '__main__':
    # Create the API wrapper
    bluevia_client = bluevia.Api(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)

    # Send an SMS
    sms_id = bluevia_client.send_sms(to='34600000000', message='Hello world!')

    # Ask for the delivery status of the sent SMS
    delivery_status = bluevia_client.get_sms_delivery_status(sms_id)
    print 'Delivery status for the SMS sent to {0}: {1}'.format(delivery_status['address'], delivery_status['status'])

    # Get SMSs sent to my app
    received_sms = bluevia_client.get_received_sms()
    for sms in received_sms:
        print 'Id:', sms['id']
        print 'From:', sms['from']
        print 'To:', sms['to']
        print 'Message', sms['message']
        print 'Timestamp', sms['timestamp']
        print

    # Send an MMS
    mms_id = bluevia_client.send_mms(to='34600000000', subject='Hello world!',
                                     attachments=('Look at this picture',
                                                  open('picture.gif', 'rb')))

    # Ask for the delivery status of the sent MMS
    delivery_status = bluevia_client.get_mms_delivery_status(mms_id)
    print 'Delivery status for the MMS sent to {0}: {1}'.format(delivery_status['address'], delivery_status['status'])

    # Get MMSs sent to my app
    received_mms = bluevia_client.get_received_mms()
    for mms_id in received_mms:
        mms = bluevia_client.get_received_mms_details(mms_id)
        print 'Id:', mms['id']
        print 'From:', mms['from']
        print 'To:', mms['to']
        print 'Subject', mms['subject']
        print 'Timestamp', mms['timestamp']
        attachments = mms['attachments']
        for attachment_index, attachment in enumerate(attachments):
            if attachment[0] == 'text/plain':
                print 'Attachment #{0}: {1}'.format(attachment_index, attachment[1])
            else:
                filename = 'attachment_{0}-{1}{2}'.format(mms_id, attachment_index,
                                                           mimetypes.guess_extension(attachment[0]))
                open(filename, 'wb').write(attachment[1])
                print 'Attachment #{0} saved to file {1}'.format(attachment_index, filename)
        print
