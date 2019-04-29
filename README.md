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
The are contained in `default.conf`, where can be changed the host, the port and whether to use multihreading or not.

### Calling the api : 

Use HTTP `GET` on the following route, while passing the binary of the file to process in the body.

```
GET :
http://host:port/numpyarray/?type=pdf&width=4096
# transform a whole document into a list of numpy arrays
# type : the type of the doc you send (default : pdf),
# width : the width in pixel you want the output array to be (default is 2048)
# The height of the output file is made so that the output keeps the same format as the original file.

GET:
http://host:port/numpyarray/?type=pdf&width=4096/:PageNumber/options
# transform one page into a numpy array
# options are the same as above

GET:
http://host:port/pagecount/options
# returns the number of pages in that document

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
