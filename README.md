# microbmp
[![PyPI version](https://badge.fury.io/py/microbmp.svg)](https://badge.fury.io/py/microbmp) [![Downloads](https://pepy.tech/badge/microbmp)](https://pepy.tech/project/microbmp)

 A simple python package for loading and saving BMP image.

Please consider [![Paypal Donate](https://github.com/jacklinquan/images/blob/master/paypal_donate_button_200x80.png)](https://www.paypal.me/jacklinquan) to support me.

## Installation
`pip install microbmp`

## Usage
```
>>> import microbmp
>>> # Create a 2(width) by 3(height) image. Pixel: img[x][y] = [r,g,b].
...
>>> img=[[[255,0,0],[0,255,0],[0,0,255]],[[255,255,0],[255,0,255],[0,255,255]]]
>>> # Save the image.
...
>>> microbmp.save_bmp_file('test.bmp', img)
>>> # Load the image.
...
>>> new_img = microbmp.load_bmp_file('test.bmp')
>>> new_img
[[[255, 0, 0], [0, 255, 0], [0, 0, 255]], [[255, 255, 0], [255, 0, 255], [0, 255, 255]]]
>>> import io
>>> bytesio = io.BytesIO()
>>> # Write bmp into BytesIO.
...
>>> microbmp.write_bmp(bytesio, img)
>>> bytesio.flush()
>>> bytesio.tell()
78
>>> bytesio.seek(0)
0
>>> bytesio.read()
b'BMN\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x02\x00\x00\x00\x03'
b'\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00'
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\xff\xff\x00\x00'
b'\x00\x00\xff\x00\xff\x00\xff\x00\x00\x00\x00\xff\x00\xff\xff\x00\x00'
```
