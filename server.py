#! /usr/bin/python
# encoding : utf-8
import argparse
import pickle

from flask import Flask, request, make_response, jsonify

from converter import get_pages, get_page, page_count, SUPPORTED_FORMAT

app = Flask(__name__)
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


@app.route("/numpyarray/<page>", methods=['GET'])
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


@app.route("/numpyarray/", methods=['GET'])
def document_to_array():
    document_type = request.args.get('type', type=str, default='pdf')
    width = request.args.get('width', type=int, default=2048)
    data = request.get_data()

    if document_type not in SUPPORTED_FORMAT:
        raise InvalidUsage("Type '{}' is not valid".format(document_type), 400)
    if not data:
        raise InvalidUsage("Missing binary", 400)
    response = get_pages(file_bin=data, file_type=document_type, width_output_file=width)
    resp_bytes = pickle.dumps(response, pickle.HIGHEST_PROTOCOL)
    return make_response(resp_bytes)


@app.route("/", methods=["GET"])
def get_types():
    return jsonify({'supported_formats': SUPPORTED_FORMAT})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='an API using PyMuPdf to turn a pdf into images')
    parser.add_argument("--host", help="host of the API (default localhost)", type=str, default='localhost')
    parser.add_argument("--port", help="port of the API (default 5000)", type=int, default=5000)
    parser.add_argument("--mono-thread",
                        help="Force flask to use of 1 thread only.",
                        action='store_true',
                        default=False)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, threaded=args.mono_thread)
