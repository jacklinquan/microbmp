# -*- coding: utf-8 -*-
"""A simple python package for loading and saving BMP image.

It works under both CPython and MicroPython.
Only uncompressed 24-bit color depth is supported.

Author: Quan Lin
License: MIT

:Example:
>>> from microbmp import load_bmp_file, save_bmp_file
>>> # Create a 2(width) by 3(height) image. Pixel: img[x][y] = [r,g,b].
>>> img=[[[255,0,0],[0,255,0],[0,0,255]],[[255,255,0],[255,0,255],[0,255,255]]]
>>> # Save the image.
>>> save_bmp_file('test.bmp', img)
>>> # Load the image.
>>> new_img = load_bmp_file('test.bmp')
"""

# Project version
__version__ = '0.1.0'
__all__ = ['read_bmp', 'write_bmp', 'load_bmp_file', 'save_bmp_file']

from struct import pack, unpack

def _get_padded_row_size(row_size):
    return (row_size + 3)//4*4

def read_bmp(file):
    """Read image from FileIO or BytesIO.
    
    :param file: io file to read from.
    :type file: FileIO or BytesIO.
    :returns: a 3D array representing an image.
    :rtype: list.
    """
    # BMP Header
    data = file.read(14)
    assert data[0:2] == b'BM', \
        'Not a valid BMP file!'
    file_size = unpack('<I', data[2:6])[0]
    offset = unpack('<I', data[10:14])[0]
    # DIB Header
    data = file.read(offset-14)
    img_width = unpack('<i', data[4:8])[0]
    img_height = unpack('<i', data[8:12])[0]
    colour_depth = unpack('<H', data[14:16])[0]
    assert colour_depth == 24, \
        'Only 24-bit color depth is supported!'
    compression = unpack('<I', data[16:20])[0]
    assert compression == 0, \
        'Compression is not supported!'
    row_size = img_width * 3
    padded_row_size = _get_padded_row_size(row_size)
    padded_img_size = padded_row_size * img_height
    img_size_info = unpack('<I', data[20:24])[0]
    if img_size_info != 0:
        assert padded_img_size == img_size_info, \
            'Image size is incorrect!'
    # Pixel Array
    img_pixels = [
        [[0,0,0] for y in range(img_height)] for x in range(img_width)
    ]
    for y in range(img_height):
        # BMP last row comes first
        h = img_height - y - 1
        data = file.read(padded_row_size)
        for x in range(img_width):
            v = x * 3
            # BMP colour is in BGR order
            img_pixels[x][h][2] = data[v]
            img_pixels[x][h][1] = data[v+1]
            img_pixels[x][h][0] = data[v+2]
    
    return img_pixels

def write_bmp(file, img_pixels):
    """Write image to FileIO or BytesIO.
    
    :param file: io file to write to.
    :type file: FileIO or BytesIO.
    :param img_pixels: a 3D array representing an image.
    :type img_pixels: list.
    """
    img_width = len(img_pixels)
    img_height = len(img_pixels[0])
    row_size = img_width * 3
    padded_row_size = _get_padded_row_size(row_size)
    padded_img_size = padded_row_size * img_height
    row_buf = bytearray(padded_row_size)
    # BMP Header
    file.write(b'BM')
    file.write(pack("<I", padded_img_size + 54))
    file.write(b'\x00\x00')
    file.write(b'\x00\x00')
    file.write(pack("<I", 54))
    # DIB Header
    file.write(pack("<I", 40))
    file.write(pack("<i", img_width))
    file.write(pack("<i", img_height))
    file.write(pack("<H", 1))
    file.write(pack("<H", 24))
    file.write(pack("<I", 0))
    file.write(pack("<I", padded_img_size))
    file.write(b'\x00' * 16)
    # Pixel Array
    for y in range(img_height):
        # BMP last row comes first
        h = img_height - y - 1
        for x in range(img_width):
            v = x * 3
            # BMP colour is in BGR order
            row_buf[v] = img_pixels[x][h][2]
            row_buf[v+1] = img_pixels[x][h][1]
            row_buf[v+2] = img_pixels[x][h][0]
        file.write(row_buf)

def load_bmp_file(file_path):
    """Load image from BMP file.
    
    :param file_path: full file path.
    :type file_path: str.
    :returns: a 3D array representing an image.
    :rtype: list.
    """
    with open(file_path, 'rb') as file:
        img_pixels = read_bmp(file)
    return img_pixels

def save_bmp_file(file_path, img_pixels):
    """Save image to BMP file.
    
    :param file_path: full file path.
    :type file_path: str.
    :param img_pixels: a 3D array representing an image.
    :type img_pixels: list.
    """
    with open(file_path, 'wb') as file:
        write_bmp(file, img_pixels)
