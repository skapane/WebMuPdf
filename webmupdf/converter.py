#!/usr/bin/python
# encoding : utf-8
import PIL.Image as pilimage
import fitz
import numpy as np

SUPPORTED_FORMAT = ['pdf', 'xps', 'oxps', 'epub', 'cbz', 'fb2', 'jpeg', 'bmp', 'jxr', 'jpx', 'gif', 'tiff', 'png',
                    'pnm', 'pgm', 'pbm', 'ppm', 'pam', 'tga', ]


def page_count(fitz_doc, filetype):
    return fitz.Document(stream=fitz_doc, filetype=filetype).pageCount


def process_one_page(fitz_doc, page_num, width_output_file):
    fitz_page = fitz_doc.loadPage(page_num)
    shape = tuple([s for s in fitz_page.MediaBox[-2:]])
    zoom_ratio = width_output_file / shape[0] if width_output_file else 2048 / shape[0]

    pm = fitz_page.getPixmap(alpha=False, matrix=fitz.Matrix(zoom_ratio, zoom_ratio))
    shape = tuple([int(s) for s in pm.irect[-2:]])
    page_as_pil = pilimage.frombytes(mode='RGB', data=pm.samples, size=shape)
    return np.array(page_as_pil)


def get_pages(file_bin, file_type, width_output_file):
    """
    convert a binary of a file into a list of numpy array.
    1 numpy array = 1 page in the document
    :param file_bin: bin. binary of the file to convert
    :param file_type: String. Extension of the file to convert
    :param width_output_file: The desired width in pixel of the output image
    :return: list(np.array)
    """
    doc = fitz.Document(stream=file_bin, filetype=file_type)
    list_of_np_img = []
    for page_num in range(doc.pageCount):
        list_of_np_img.append(process_one_page(fitz_doc=doc, page_num=page_num, width_output_file=width_output_file))
    return list_of_np_img


def get_page(file_bin, page_num, file_type, width_output_file):
    return process_one_page(
        fitz_doc=fitz.Document(stream=file_bin, filetype=file_type),
        page_num=page_num,
        width_output_file=width_output_file
    )
