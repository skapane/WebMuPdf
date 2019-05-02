#! /usr/bin/python
# encoding : utf-8
import ConfigParser
import os
import pickle
import site
import sys
import time

from flask import Flask
from flask import request, make_response, jsonify

from converter import get_pages, get_page, page_count, SUPPORTED_FORMAT

app = Flask("webmupdf")
app.url_map.strict_slashes = False


class InvalidUsage(Exception):
    """
    from flask documentation :
    http://flask.pocoo.org/docs/1.0/patterns/apierrors/
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    from flask documentation :
    http://flask.pocoo.org/docs/1.0/patterns/apierrors/
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/pagecount/", methods=['GET'])
def get_page_count():
    document_type = request.args.get('type', type=str, default='pdf')
    data = request.get_data()
    return jsonify({'length': page_count(data, document_type)})


@app.route("/numpyarray/<page>", methods=['POST'])
def one_page_to_array(page):
    page = int(page)
    document_type = request.args.get('type', type=str, default='pdf')
    width = request.args.get('width', type=int, default=2048)
    data = request.get_data()

    if document_type not in SUPPORTED_FORMAT:
        raise InvalidUsage("Type '{}' is not valid".format(document_type), 400)
    if not data:
        raise InvalidUsage("Missing binary", 400)
    response = get_page(file_bin=data, page_num=page, file_type=document_type, width_output_file=width)
    resp_bytes = pickle.dumps(response, pickle.HIGHEST_PROTOCOL)
    return make_response(resp_bytes)


@app.route("/numpyarray/", methods=['POST'])
def document_to_array():
    start = time.time()
    document_type = request.args.get('type', type=str, default='pdf')
    width = request.args.get('width', type=int, default=2048)
    data = request.get_data()

    if document_type not in SUPPORTED_FORMAT:
        raise InvalidUsage("Type '{}' is not valid".format(document_type), 400)
    if not data:
        raise InvalidUsage("Missing binary", 400)

    response = get_pages(file_bin=data, file_type=document_type, width_output_file=width)
    resp_bytes = pickle.dumps(response, pickle.HIGHEST_PROTOCOL)
    print 'time : {}'.format(time.time() - start)
    print 'Size to send : {}'.format(sys.getsizeof(resp_bytes))
    return make_response(resp_bytes)


@app.route("/", methods=["GET"])
def get_types():
    return jsonify({'supported_formats': SUPPORTED_FORMAT})


if __name__ == '__main__':
    FOLDER_DATA = 'share'
    conf = ConfigParser.ConfigParser()
    print sys.prefix, site.USER_BASE
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

    elif os.path.exists(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),  '../webmupdf.conf')):

        path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),  '../webmupdf.conf')
        print('loading conf from {}'.format(path))
        conf.read(path)
    else:
        print os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),  '../webmupdf.conf')
        raise IOError("webmupdf.conf not found")

    app.run(
        host=conf.get('api', 'host'),
        port=conf.getint('api', 'port'),
        threaded=True,
    )
