import ConfigParser
import os
import site
import sys

from webmupdf import app

conf = ConfigParser.ConfigParser()

if os.path.exists(os.path.join(sys.prefix, '/share/webmupdf.conf')):
    path = os.path.join(sys.prefix + '/share/webmupdf.conf')
    print('loading conf from {}'.format(path))
    conf.read(path)
else:
    try:
        path = os.path.join(site.USER_BASE, 'share/webmupdf.conf')
        print('loading conf from {}'.format(path))
        conf.read(path)
    except ConfigParser.NoSectionError:
        raise IOError("webmupdf.conf not found")

app.run(
    host=conf.get('api', 'host'),
    port=conf.getint('api', 'port'),
    threaded=conf.getboolean('api', 'mono_thread')
)
