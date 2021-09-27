#!/usr/bin/python
# encoding : utf-8
import PIL.Image as Image
import fitz
import numpy as np
import subprocess
from webmupdf.kernel import ConvertedPage
from io import BytesIO

SUPPORTED_FORMAT = ['pdf', 'xps', 'oxps', 'epub', 'cbz', 'fb2', 'jpeg', 'bmp', 'jxr', 'jpx', 'gif', 'tiff', 'png',
                    'pnm', 'pgm', 'pbm', 'ppm', 'pam', 'tga', ]


def page_count(fitz_doc, filetype):
    return fitz.Document(stream=fitz_doc, filetype=filetype).pageCount


def render_page(smallest_side, fitz_page, width_output_file):
    zoom_ratio = width_output_file / smallest_side if width_output_file else 2048 / smallest_side

    pm = fitz_page.getPixmap(alpha=False, matrix=fitz.Matrix(zoom_ratio, zoom_ratio))
    shape = tuple([int(s) for s in pm.irect[-2:]])
    page_as_pil = Image.frombytes(mode='RGB', data=pm.samples, size=shape)
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
        smallest_side = min(page.CropBox.height, page.CropBox.width)
        list_of_np_img.append(render_page(
            smallest_side=smallest_side,
            fitz_page=page,
            width_output_file=width_output_file
        ))
    return list_of_np_img


def get_page(file_bin, page_num, file_type, width_output_file):
    """
    :return: A converted page containing the render and text data
    """
    doc = fitz.Document(stream=file_bin, filetype=file_type)
    page = doc.loadPage(page_num)

    # Use page object to get page height and width
    page_height = page.MediaBoxSize.y
    page_width = page.MediaBoxSize.x
    page_area = page_height * page_width

    smallest_side = min(page_height, page_width)

    # Get blocks with image bboxes only (no actual image is loaded)
    blocks = page.getText('BLOCKS', flags=7)

    # Check if images represent a big portion of the page's area
    # Also check that there is text in the block level data
    there_is_text_embedded = False
    text = ""
    images_area = 0
    text_area = 0
    images_position = []
    for block in blocks:
        # if this is a text block
        if block[6] == 0:
            # update there_is_text_embedded if text is not whitespaces or weird question mark �
            stripped_text = block[4].strip()
            if stripped_text != "":
                text += stripped_text
                there_is_text_embedded = True
                block_height = block[3] - block[1]
                block_width = block[2] - block[0]
                text_area += block_height * block_width
        # if this is an image block
        if block[6] == 1:
            # add area of image to total area
            block_height = block[3] - block[1]
            block_width = block[2] - block[0]
            images_area += block_height * block_width
            images_position.append({
                u"left": block[0],
                u"top": block[1],
                u"width": block_width,
                u"height": block_height,
            })

    images_are_minority = images_area < (0.5 * page_area)

    # test for weird random text
    spec_rate = 0.0
    if there_is_text_embedded:
        spec_rate = len([c for c in text if not c.isalnum()]) / len(text)

    use_generated_pdf = (
            images_are_minority
            and there_is_text_embedded
            and spec_rate < 0.5
            and text_area > images_area
    )

    generated_pdf_data = {
        'words': [],
        'width': 0,
        'images': images_position,
    }

    # Transform raw data extracted from the pdf into structured dict generated_pdf_data
    if use_generated_pdf:
        words = page.getText('WORDS', 0)  # this 0 argument excludes whitespaces and extends ligatures
        generated_pdf_data['width'] = page_width
        generated_pdf_data['words'] = [
            {
                u"position": {
                    u"left": word[0],
                    u"top": word[1],
                    u"width": word[2] - word[0],
                    u"height": word[3] - word[1],
                },
                u"text": word[4],
                u"block_num": word[5],
                u"word_num": word[7],
            }
            for word in words
        ]

        # Exception for when doc is hopeless
        if (
                set([font_tuple[3] for font_tuple in doc.getPageFontList(page_num)]) == set(['TimesNewRomanPSMT', 'TimesNewRomanPS-BoldMT']) and
                all(
                    all(char == "�" for char in word["text"].strip())
                    for word in generated_pdf_data['words']
                )
        ):
            return get_page_with_pdftoppm(file_bin, page_num, width_output_file)

    np_array = render_page(
        smallest_side=smallest_side,
        fitz_page=page,
        width_output_file=width_output_file
    )

    return ConvertedPage(np_array, generated_pdf_data)


def get_page_with_pdftoppm(file_bin, page_num, target_width):
    process = subprocess.Popen(
        [
            "pdftoppm",
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            "-png",
            "-r",
            "300",
            "-scale-to-x",
            str(target_width),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    out, err = process.communicate(file_bin)
    with Image.open(BytesIO(out)) as image:
        return ConvertedPage(np.array(image), {"words": [], "width": 0})
