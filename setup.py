import setuptools
import sys

print sys.prefix
FOLDER_DATA = './share'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webmupdf",
    version="0.0.1",
    author="Nathan Malnoury",
    author_email="nmalnoury@skapane.com",
    description="A web service for PyMuPDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skapane/WebMuPdf",
    packages=['webmupdf'],
    include_package_data=True,
    install_requires=[
        "click==7.0",
        "flask==1.0.2",
        "itsdangerous==1.1.0",
        "jinja2==2.10.1",
        "markupsafe==1.1.1",
        "numpy==1.16.2",
        "pillow==5.3.0",
        "pymupdf==1.14.13",
        "werkzeug==0.15.2",
    ],
    data_files=[(FOLDER_DATA, ['./webmupdf.conf', './webmupdf.wsgi'])],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: GPL v3",
        "Operating System :: OS Independent",
    ],
)
