#!/usr/bin/python
# encoding : utf-8
import PIL.Image as pilimage
import fitz
import numpy as np

from webmupdf.kernel import ConvertedPage

SUPPORTED_FORMAT = ['pdf', 'xps', 'oxps', 'epub', 'cbz', 'fb2', 'jpeg', 'bmp', 'jxr', 'jpx', 'gif', 'tiff', 'png',
                    'pnm', 'pgm', 'pbm', 'ppm', 'pam', 'tga', ]


def page_count(fitz_doc, filetype):
    return fitz.Document(stream=fitz_doc, filetype=filetype).pageCount


def render_page(fitz_page, width_output_file):
    shape = tuple([s for s in fitz_page.MediaBox[-2:]])
    width, height = min(shape), max(shape)
    zoom_ratio = width_output_file / width if width_output_file else 2048 / width

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
        page = doc.loadPage(page_num)
        list_of_np_img.append(render_page(fitz_page=page, width_output_file=width_output_file))
    return list_of_np_img


def get_page(file_bin, page_num, file_type, width_output_file):
    """
    :return: A converted page containing the render and text data
    """
    doc = fitz.Document(stream=file_bin, filetype=file_type)
    page = doc.loadPage(page_num)

    data = []

    dicts = page.getText("dict")
    for bbox in dicts["blocks"]:
        if bbox.has_key("lines"):
            for subbbox in bbox["lines"]:
                if subbbox.has_key("spans"):
                    myspan = []
                    for spans in subbbox["spans"]:
                        txt = spans.get("text", u"").strip()
                        if txt:
                            myspan.append(spans)
                    if myspan:
                        subbbox["spans"] = myspan
                        data.append(subbbox)

    dicts["blocks"] = data
    
    np_array = render_page(
        fitz_page=page,
        width_output_file=width_output_file
    )

    return ConvertedPage(np_array, dicts)
