#!/bin/python
# encoding: utf8


class ConvertedPage(object):
    def __init__(self, np_render, block_data):
        """
        :type page_type: PageTypes
        """
        self.np_render = np_render
        self.block_data = block_data

