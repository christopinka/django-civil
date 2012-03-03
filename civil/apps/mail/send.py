# -*- coding: utf-8 -*-

import os
from django.conf import settings

from email import Encoders, mime
from BeautifulSoup import BeautifulSoup


#==============================================================================
def send_mail(smtp, sender, destination, subject, htmlbody, textbody, attachments=[], reply_to=None):
    """
        Send a mail using a smtp server already connected and logged
    """

    # Create the root message and fill in the from, to, and subject headers
    msg = mime.multipart.MIMEMultipart('related')
    msg['From'] = sender
    msg['To'] = destination
    msg['Subject'] = subject
    msg.add_header('Reply-To', reply_to if reply_to else sender)

    # Convert html images cids
    def load_file_data(path):
        filedata = None
        if path.startswith(settings.FILEBROWSER_DIRECTORY):
            path = "%s%s" % (settings.MEDIA_URL, path)
        if path.startswith(settings.MEDIA_URL):
            path = path[len(settings.MEDIA_URL):]
            fp = open("%s/%s" % (settings.MEDIA_ROOT, path), 'rb')
            filedata = fp.read()
            fp.close()
        elif path.startswith(settings.STATIC_URL):
            path = path[len(settings.STATIC_URL):]
            fp = open("%s/%s" % (settings.STATIC_ROOT, path), 'rb')
            filedata = fp.read()
            fp.close()
        elif path.startswith('http://') or path.startswith('ftp://'):
            import urllib2
            response = urllib2.urlopen(path)
            filedata = response.read()
            # TODO - check if this is enough
        else:
            pass # TODO - what should i do here ?
        return filedata

    soup = BeautifulSoup(htmlbody, isHTML=True)
    
    images = soup.findAll('img')
    images_data = []
    images_count = 0
    for img in images:
        path = img['src']
        fileData = load_file_data(path)
        if fileData:
            images_data.append(fileData)
            img['src'] = 'cid:image%s' % images_count
            images_count += 1
            
    links = soup.findAll('a')             
    for link in links:
        path = link['href']
        if not path.startswith('http://'):
            if path.startswith('/'): path = path[1:]
            # TODO - make the server name absolute !
            link['href'] = "http://www.canipercaso.it/%s" % path

    htmlbody = soup.prettify()
    
    # Encapsulate the plain and HTML versions of the message body in an
    # alternative part, so message agents can decide which they want to display.
    msg_alt = mime.multipart.MIMEMultipart('alternative')
    msg.attach(msg_alt)
    # TODO - handle when no text or html is defined
    if textbody:
        msg_text = mime.text.MIMEText(textbody)
        msg_alt.attach(msg_text)
    if htmlbody:
        msg_html = mime.text.MIMEText(htmlbody, 'html', 'utf-8')
        msg_alt.attach(msg_html)

    # Merge images in mime
    images_count = 0
    for fileData in images_data:
        msg_image = mime.image.MIMEImage(fileData)
        msg_image.add_header('Content-ID', '<image%s>' % images_count)
        msg.attach(msg_image)
        images_count += 1

    # Add attachments
    for f in attachments:
        path = f.file.path
        fileData = load_file_data(path)
        if fileData:
            msg_base = mime.base.MIMEBase('application', 'octet-stream')
            msg_base.set_payload(fileData)
            Encoders.encode_base64(msg_base)
            msg_base.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(path))
            msg.attach(msg_base)
    
    if smtp:
        smtp.sendmail(sender, destination, msg.as_string())
    else:
        pass # TODO - log this somewhere
