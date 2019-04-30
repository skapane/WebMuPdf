#!/usr/bin/python
# encoding : utf-8
import ConfigParser
import os
import site
import sys

from webmupdf import app

FOLDER_DATA = 'share'
conf = ConfigParser.ConfigParser()

if os.path.exists(os.path.join(sys.prefix, FOLDER_DATA, 'webmupdf.conf')):
    path = os.path.join(sys.prefix, FOLDER_DATA, 'webmupdf.conf')
    print('loading conf from {}'.format(path))
    conf.read(path)

elif os.path.exists(os.path.join(sys.prefix, 'local', FOLDER_DATA, 'webmupdf.conf')):
    path = os.path.join(sys.prefix, 'local', FOLDER_DATA, 'webmupdf.conf')
    print('loading conf from {}'.format(path))
    conf.read(path)

elif os.path.exists(os.path.join(site.USER_BASE, FOLDER_DATA, 'webmupdf.conf')):
    path = os.path.join(site.USER_BASE, FOLDER_DATA, 'webmupdf.conf')
    print('loading conf from {}'.format(path))
    conf.read(path)
else:
    raise IOError("webmupdf.conf not found")

app.run(
    host=conf.get('api', 'host'),
    port=conf.getint('api', 'port'),
    threaded=True,
)
