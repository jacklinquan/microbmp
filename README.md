# microbmp
[![PyPI version](https://badge.fury.io/py/microbmp.svg)](https://badge.fury.io/py/microbmp) [![Downloads](https://pepy.tech/badge/microbmp)](https://pepy.tech/project/microbmp)

A simple python package for loading and saving BMP image.
 
It works under both CPython and MicroPython. BMP image of 1/2/4/8/24-bit color depth is supported.

Loading supports compression method:
- 0(BI_RGB, no compression)
- 1(BI_RLE8, RLE 8-bit/pixel)
- 2(BI_RLE4, RLE 4-bit/pixel)

Saving only supports compression method 0(BI_RGB, no compression).

Please consider [![Paypal Donate](https://github.com/jacklinquan/images/blob/master/paypal_donate_button_200x80.png)](https://www.paypal.me/jacklinquan) to support me.

## Installation
`pip install microbmp`

## Usage
```Python
>>> from microbmp import MicroBMP
>>> img_24b = MicroBMP(2, 2, 24) # Create a 2(width) by 2(height) 24-bit image.
>>> img_24b.palette # 24-bit image has no palette.
>>> img_24b.pixels # img_24b.pixels[x][y] = [r, g, b]
[[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]]
>>> img_24b.pixels = [[[0,0,255], [255,0,0]], [[0,255,0], [255,255,255]]]
>>> img_24b.save('img_24b.bmp')
70
>>> new_img_24b = MicroBMP().load('img_24b.bmp')
>>> new_img_24b.palette
>>> new_img_24b.pixels
[[[0, 0, 255], [255, 0, 0]], [[0, 255, 0], [255, 255, 255]]]
>>> img_1b = MicroBMP(3, 2, 1) # Create a 3(width) by 2(height) 1-bit image.
>>> img_1b.palette # img_1b.palette[index] = [r, g, b]
[[0, 0, 0], [255, 255, 255]]
>>> img_1b.pixels # img_1b.pixels[x][y] = index
[[0, 0], [0, 0], [0, 0]]
>>> img_1b.pixels = [[0, 0], [1, 1], [0, 1]]
>>> img_1b.save('img_1b.bmp')
70
>>> new_img_1b = MicroBMP().load('img_1b.bmp')
>>> new_img_1b.palette
[[0, 0, 0], [255, 255, 255]]
>>> new_img_1b.pixels
[[0, 0], [1, 1], [0, 1]]
```
