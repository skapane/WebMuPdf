# WebMuPdf :

A web client for WebMuPdf.
first implementation converts any supported file into a numpy array.


**This project license is GNU GPL v3** (PyMuPDF is distributed under GNU GPL V3. MuPDF is distributed under the GNU AFFERO GPL V3.)

## Installation :

Developed for python 2.7, this code should also run smoothly with python 3.7.

### Step 1 : Clone project
```bash
$ git clone ...
```

### Step 2: Install requirements :
```bash
$ cd yourpath/WebMuPdf
$ pip install -r requirements.txt
```

### Step 3: run server.py : 

Two choices : 1 : run server with Flask, 2 : running server.py

* Run server with flask : 

Create a flask variable :
```bash
$ export FLASK_APP=/pathtoproject/server.py
```
To run the api, execute : 
```bash
$ flask run
```
*this technique is useful if you want to run the app from anywhere, and by exporting `FLASK_APP` in your .bashrc, it becames fully automated*

----

* Running server.py

Simply call the programm : 
```bash
$ /pathtoproject/server.py
```

## Using the API :

### Parameters : 
Calling `server.py --help` shows you all the variable you can choose : 

```bash
$ python ./projects/WebMuPdf/server.py --help
usage: server.py [-h] [--host HOST] [--port PORT] [--mono-thread] [--list]

an API using PyMuPdf to turn a pdf into images

optional arguments:
  -h, --help     show this help message and exit
  --host HOST    host of the API (default localhost)
  --port PORT    port of the API (default 5000)
  --mono-thread  Force the use of 1 thread only.
  --list         return the supported file types.

```

### Calling the api : 

Use HTTP `POST` on the following route, while passing the binary of the file to process in the body.

```
http://host:port/toArray/?type=pdf&width=4096

# type : the type of the doc you send (default : pdf),
# width : the width in pixel you want the output array to be (default is 2048)
# The height of the output file is made so that the output keeps the same format as the original file.
```

The API returns a pickle object. To use the API in an other software piece : 

```python
import requests
import pickle
import os

FILEPATH =  '/path/to/file.ext'
WIDTH_IN_PIXEL = 2048
extension = os.path.basename(FILEPATH).split('.')[-1]
with open(FILEPATH, 'rb') as f:
    bin = f.read()

r = requests.get(
    "http://127.0.0.1:5000/numpyarray/?type={}&width={}".format(extension, WIDTH_IN_PIXEL),
    data=bin
)

arr = pickle.loads(r.content)
```

## Supported files :
They are accessible by running the following command : 
```bash
$ ./pathtoprojects/server.py --list
['pdf', 'xps', 'oxps', 'epub', 'cbz', 'fb2', 'jpeg', 'bmp', 'jxr', 'jpx', 'gif', 'tiff', 'png', 'pnm', 'pgm', 'pbm', 'ppm', 'pam', 'tga']

```
# WebMuPdf
