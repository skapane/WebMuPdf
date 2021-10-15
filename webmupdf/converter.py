#!/usr/bin/python
# encoding : utf-8
import sys

import fitz
import numpy as np
import PIL.Image as Image
import subprocess

from io import BytesIO
from typing import List, Tuple

from webmupdf.kernel import ConvertedPage

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


def get_page(file_bin, page_num, file_type, width_output_file, password):
    """
    :return: A converted page containing the render and text data
    """
    doc = fitz.Document(stream=file_bin, filetype=file_type)
    if doc.isEncrypted and password is not None:
        doc.authenticate(password)
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
        directions = get_letter_orientation(page)
        generated_pdf_data['width'] = page_width

        index = 0
        orientations = []

        for word in words:
            len_word = len(word[4])
            try:
                orientations.append(directions[index])
                index = index + len_word
            except IndexError:
                print('ERROR: The length of "words" is longer than the length of "directions".', file=sys.stderr)
                orientations = [0] * len(words)
                break

        if index != len(directions):
            print('ERROR: The length of "directions" is longer than the length of "words".', file=sys.stderr)
            orientations = [0] * len(words)

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
                u"orientation": orientations[index]
            }
            for index, word in enumerate(words)
        ]

        # Exception for when doc is hopeless
        if (
                set(
                    [font_tuple[3] for font_tuple in doc.getPageFontList(page_num)]
                ) == {'TimesNewRomanPSMT', 'TimesNewRomanPS-BoldMT'}
                and all(
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


def get_letter_orientation(page):
    # type: (fitz.fitz.Document.loadPage) -> List[int]
    """
    Get the orientation of each individual letter.

    :param page: a Page element loaded to a fitz.Document.
    :return: a list of tuples each containing the letter and its orientation in the page (0: horizontal, 1: vertical).
    """

    def determine_direction(line_direction):
        # type: (Tuple[float, float]) -> int
        """
        Determines the direction of each line extracted from the generated pdf.

        :param line_direction: the direction of the line as provided by line["dir"].
        :return: an int indicating its direction: 0 for horizontal (default), 1 for vertical and 2 for diagonal.
        """

        direction_ = 0  # horizontal text by default

        if line_direction and isinstance(line_direction[0], float) and isinstance(line_direction[1], float):
            if line_direction in [(0.0, 1.0), (0.0, -1.0)]:
                direction_ = 1  # vertical text
            elif line_direction != (1.0, 0.0):
                direction_ = 2  # diagonal text

        return direction_

    text_dict = page.getText('DICT')

    result = []
    for block in text_dict["blocks"]:
        if "lines" in block.keys():
            for line in block["lines"]:
                if isinstance(line, list):
                    for individual_line in line:
                        for span in individual_line["spans"]:
                            direction = determine_direction(individual_line["dir"])
                            result += [direction] * len(span["text"].replace(" ", ""))
                else:
                    for span in line["spans"]:
                        direction = determine_direction(line["dir"])
                        result += [direction] * len(span["text"].replace(" ", ""))

    return result
