#! /usr/bin/python
# encoding : utf-8
import argparse

from webmupdf.split import split_pages

try:
    import cPickle as pickle
except ImportError:
    import pickle
import sys

import webmupdf.converter as converter

try:
    sys_stdin = sys.stdin.buffer
    sys_stdout = sys.stdout.buffer
except AttributeError:
    sys_stdin = sys.stdin
    sys_stdout = sys.stdout

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Transforms pdf into numpy arrays')
    parser.add_argument("--type", help="Type of document (pdf, png, jpeg, ...)", type=str, default='pdf')
    parser.add_argument("--width", help="Width in pixel of the output document", type=int, default=2048)
    parser.add_argument("--page", help='if only one page to process, use this argument. Pages are indexed from 0',
                        type=int, default=-1)
    parser.add_argument("--start_page", help='Number of the first page to start splitting at', type=int, default=0)
    parser.add_argument("--end_page", help='Number of the last page (included) to stop splitting at', type=int,
                        default=0)
    parser.add_argument("--page-count", help='count number of pages in a document', action='store_true', default=False)
    parser.add_argument("--output", help='Type of output to give', type=str, default="np_array",
                        choices=["np_array", "ConvertedPage", "pdf_document"])
    args = parser.parse_args()
    file_binary = sys_stdin.read()

    if args.page_count:
        sys.stdout.write(str(converter.page_count(file_binary, filetype=args.type)))

    elif args.page != -1:

        if args.output == "pdf_document":
            pdf_file = split_pages(file_bin=file_binary,
                                   start_page_num=args.start_page,
                                   end_page_num=args.end_page,
                                   file_type=args.type)
            sys_stdout.write(pickle.dumps(
                    pdf_file,
                    pickle.HIGHEST_PROTOCOL
                ))

        else:
            # user sent a page to be converted
            converted_page = converter.get_page(
                file_bin=file_binary,
                file_type=args.type,
                page_num=args.page,
                width_output_file=args.width
            )

            if args.output == "ConvertedPage":
                sys_stdout.write(pickle.dumps(
                    converted_page,
                    pickle.HIGHEST_PROTOCOL
                ))
            elif args.output == "np_array":
                sys_stdout.write(pickle.dumps(
                    converted_page.np_render,
                    pickle.HIGHEST_PROTOCOL
                ))