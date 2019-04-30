import setuptools

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
    install_requires=['flask'],
    data_files=[('share', ['./webmupdf.conf'])],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: GPL v3",
        "Operating System :: OS Independent",
    ],
)
