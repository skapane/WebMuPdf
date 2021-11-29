import setuptools

setuptools.setup(
    name="webmupdf",
    version="2.2.0",
    author="Nathan Malnoury, Yassine Fikrat, Renaud Loiseleux",
    description="A web service for PyMuPDF",
    long_description_content_type="text/markdown",
    url="https://github.com/skapane/WebMuPdf",
    packages=['webmupdf'],
    include_package_data=True,
    install_requires=[
        "numpy==1.20.3",
        "pillow==7.1.2",
        "pymupdf~=1.16.10",
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3.7",
        "License :: GPL v3",
        "Operating System :: OS Independent",
    ],
)
