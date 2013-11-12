# -*- coding: utf-8 -*-
import mimetypes
from email import encoders
from email.utils import COMMASPACE
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from boto.ses import SESConnection
from ig_api import app

## boto SES connection
connection = SESConnection(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

class SESMessage(object):
    """
    Usage:
    
    msg = SESMessage('from@example.com', 'to@example.com', 'The subject')
    msg.text = 'Text body'
    msg.html = 'HTML body'
    msg.send()
    
    """
    
    def __init__(self, source, to_addresses, subject, **kw):
        self.ses = connection
        
        self._source = source
        self._to_addresses = to_addresses
        self._cc_addresses = None
        self._bcc_addresses = None

        self.subject = subject
        self.text = None
        self.html = None
        self.attachments = []

    def send(self):
        if not self.ses:
            raise Exception, 'No connection found'
        
        if (self.text and not self.html and not self.attachments) or \
           (self.html and not self.text and not self.attachments):
            return self.ses.send_email(self._source, self.subject,
                                       self.text or self.html,
                                       self._to_addresses, self._cc_addresses,
                                       self._bcc_addresses,
                                       format='text' if self.text else 'html')
        else:
            message = MIMEMultipart('alternative')
            
            message['Subject'] = self.subject
            message['From'] = self._source
            if isinstance(self._to_addresses, (list, tuple)):
                message['To'] = COMMASPACE.join(self._to_addresses)
            else:
                message['To'] = self._to_addresses
            
            message.attach(MIMEText(self.text, 'plain'))
            message.attach(MIMEText(self.html, 'html'))
