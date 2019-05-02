#! /usr/bin/python
# encoding : utf-8
import argparse
import pickle
import sys

import webmupdf.converter as converter

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Transforms pdf into numpy arrays')
    parser.add_argument("--type", help="Type of document (pdf, png, jpeg, ...)", type=str, default='pdf')
    parser.add_argument("--width", help="Width in pixel of the output document", type=int, default=2048)
    parser.add_argument("--page", help='if only one page to process, use this argument. Pages are indexed from 0',
                        type=int, default=-1)
    parser.add_argument("--page-count", help='count number of pages in a document', action='store_true', default=False)
    args = parser.parse_args()
    file_binary = sys.stdin.read()

    if args.page_count:
        sys.stdout.write(pickle.dumps(converter.page_count(file_binary, filetype=args.type), pickle.HIGHEST_PROTOCOL))

    if args.page != -1:
        # user sent a page to be converted
        np_img = converter.get_page(file_bin=file_binary, file_type=args.type, page_num=args.page, width_output_file=args.width)
        sys.stdout.write(pickle.dump(np_img, pickle.HIGHEST_PROTOCOL))

    np_array = converter.get_pages(file_bin=file_binary, file_type=args.type, width_output_file=args.width)
    sys.stdout.write(pickle.dumps(np_array, pickle.HIGHEST_PROTOCOL))