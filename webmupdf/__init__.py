#!/usr/bin/python
# encoding : utf-8
from flask import Flask

app = Flask("webmupdf")
app.url_map.strict_slashes = False

from webmupdf import server
