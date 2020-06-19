# WebMuPdf :

A web client for WebMuPdf.
first implementation converts any supported file into a numpy array.


**This project license is GNU GPL v3** (PyMuPDF is distributed under GNU GPL V3. MuPDF is distributed under the GNU AFFERO GPL V3.)

## Installation as a package :
### Step 1 : Clone project
```bash
$ git clone https://github.com/skapane/WebMuPdf.git
```

### Step 2 : installing as a package
```bash
$ pip install /path/toproject/ --user
```

Please note that a configuration file is created in either /usr/local or ~/.local.
### Step 3 : running the lib:

As a cli call:
```bash
$ python -m webmupdf.cli 
```
In this configuration, options are given in the command (you can see them by --help)
The binary is expected in the stdin.

## Installation as a script:

Developed for python 2.7, this code should also run smoothly with python 3.7.

### Step 1 : Clone project
```bash
$ git clone https://github.com/skapane/WebMuPdf.git
```

### Step 2: Install requirements :
```bash
$ cd yourpath/webmupdf
$ pip install -r requirements.txt
```


