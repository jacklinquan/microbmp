# microbmp
A small Python module for BMP image processing.
 
It supports BMP image of 1/2/4/8/24-bit colour depth.

Loading supports compression method:

- 0(BI_RGB, no compression)
- 1(BI_RLE8, RLE 8-bit/pixel)
- 2(BI_RLE4, RLE 4-bit/pixel)

Saving only supports compression method 0(BI_RGB, no compression).

## Installation
`pip install microbmp`

## Usage
```Python
>>> from microbmp import MicroBMP
>>> img_24b_2x2 = MicroBMP(2, 2, 24)  # Create a 2(width) by 2(height) 24-bit image.
>>> img_24b_2x2.palette  # 24-bit image has no palette.
>>> img_24b_2x2.parray  # Pixels are arranged horizontally (top-down) in RGB order.
bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
>>> img_24b_2x2[1, 1] = 255, 255, 255  # Access 1 pixel (R, G, B): img[x, y]
>>> img_24b_2x2[0, 1, 0] = 255  # Access 1 primary colour of 1 pixel (Red): img[x, y, c]
>>> img_24b_2x2[1, 0, 1] = 255  # (Green)
>>> img_24b_2x2[0, 0, 2] = 255  # (Blue)
>>> img_24b_2x2.save("img_24b_2x2.bmp")
70
>>> new_img_24b_2x2 = MicroBMP().load("img_24b_2x2.bmp")
>>> new_img_24b_2x2.palette
>>> new_img_24b_2x2.parray
bytearray(b'\x00\x00\xff\x00\xff\x00\xff\x00\x00\xff\xff\xff')
>>> print(new_img_24b_2x2)
BMP image, RGB, 24-bit, 2x2 pixels, 70 bytes
>>> img_1b_3x2 = MicroBMP(3, 2, 1)  # Create a 3(width) by 2(height) 1-bit image.
>>> img_1b_3x2.palette  # Each colour is in the order of (R, G, B)
[bytearray(b'\x00\x00\x00'), bytearray(b'\xff\xff\xff')]
>>> img_1b_3x2.parray  # Each bit stores the colour index in HLSB format.
bytearray(b'\x00')
>>> " ".join([f"{bin(byte)[2:]:0>8}" for byte in img_1b_3x2.parray])
'00000000'
>>> img_1b_3x2[1, 0] = 1  # Access 1 pixel (index): img[x, y]
>>> img_1b_3x2[1, 1] = 1
>>> img_1b_3x2[2, 1] = 1
>>> img_1b_3x2.save("img_1b_3x2.bmp")
70
>>> new_img_1b_3x2 = MicroBMP().load("img_1b_3x2.bmp")
>>> new_img_1b_3x2.palette
[bytearray(b'\x00\x00\x00'), bytearray(b'\xff\xff\xff')]
>>> new_img_1b_3x2.parray
bytearray(b'L')
>>> " ".join([f"{bin(b)[2:]:0>8}" for b in new_img_1b_3x2.parray])
'01001100'
>>> print(new_img_1b_3x2)
BMP image, indexed, 1-bit, 3x2 pixels, 70 bytes
```

## Change
- Version 0.3.0
    - Implementation of palette and pixels storage is changed from list to bytearray.
    - API for pixel accessing is changed.
