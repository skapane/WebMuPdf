import setuptools

FOLDER_DATA = './share'

setuptools.setup(
    name="webmupdf",
    version="1.0.0",
    author="Nathan Malnoury, Yassine Fikrat",
    description="A web service for PyMuPDF",
    long_description_content_type="text/markdown",
    url="https://github.com/skapane/WebMuPdf",
    packages=['webmupdf'],
    include_package_data=True,
    install_requires=[
        "flask==1.0.2",
        "numpy==1.16.2",
        "pillow==5.3.0",
        "pymupdf~=1.16.10",
    ],
    data_files=[(FOLDER_DATA, ['./webmupdf.conf', './webmupdf.wsgi'])],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: GPL v3",
        "Operating System :: OS Independent",
    ],
)
