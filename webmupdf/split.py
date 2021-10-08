#!/usr/bin/python
# encoding : utf-8

import fitz


def split_pages(file_bin, start_page_num, end_page_num, file_type):
    # type: (bytes, int, int, str) -> bytes
    """
    Splits a file using a range of pages.

    :param file_bin: File in bytes.
    :param start_page_num: Page to start splitting from.
    :param end_page_num: Page to stop splitting to.
    :param file_type: Type of the file.
    :return: The split file in bytes.
    """

    doc = fitz.Document(stream=file_bin, filetype=file_type)
    doc.select(range(start_page_num, end_page_num + 1))

    return doc.write(deflate=1)
