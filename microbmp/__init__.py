# -*- coding: utf-8 -*-
"""A simple python package for loading and saving BMP image.

It works under both CPython and MicroPython.
BMP image of 1/2/4/8/24-bit color depth is supported.
Loading supports compression method:
    0(BI_RGB, no compression)
    1(BI_RLE8, RLE 8-bit/pixel)
    2(BI_RLE4, RLE 4-bit/pixel)
Saving only supports compression method 0(BI_RGB, no compression).

Author: Quan Lin
License: MIT

:Example:
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
"""

# Project Version
__version__ = '0.2.0'
__all__ = ['MicroBMP']

from struct import pack, unpack

class MicroBMP(object):
    """MicroBMP image class.
    
    :param width: image width.
    :type width: int.
    :param height: image height.
    :type height: int.
    :param depth: image colour depth.
    :type depth: int, valid values are 1/2/4/8/24.
    :param palette: image palette if applicable.
    :type palette: list of colours.
    """
    def __init__(self, width=None, height=None, depth=None, palette=None):
        # BMP Header
        self.BMP_id = b'BM'
        self.BMP_size = None
        self.BMP_reserved1 = b'\x00\x00'
        self.BMP_reserved2 = b'\x00\x00'
        self.BMP_offset = None
        
        # DIB Header
        self.DIB_len = 40
        self.DIB_w = width
        self.DIB_h = height
        self.DIB_planes_num = 1
        self.DIB_depth = depth
        self.DIB_comp = 0
        self.DIB_raw_size = None
        self.DIB_hres = 2835 # 72 DPI * 39.3701 inches/metre.
        self.DIB_vres = 2835
        self.DIB_num_in_plt = None
        self.DIB_extra = None
        
        self.palette = palette
        self.pixels = None
        
        self.ppb = None # Number of pixels per byte for depth <= 8.
        self.row_size = None
        self.padded_row_size = None
        
        self.initialised = False
        self.init()
        
    def init(self):
        """Initialize the image.
        
        :returns: successfully initialized the image or not.
        :rtype: bool.
        """
        if None in (self.DIB_w, self.DIB_h, self.DIB_depth):
            self.initialised = False
            return self.initialised
        
        assert self.BMP_id == b'BM', \
            'BMP id ({}) must be b\'BM\'!'.format(self.BMP_id)
        assert len(self.BMP_reserved1) == 2 and len(self.BMP_reserved2) == 2, \
            'Length of BMP reserved fields ({}+{}) must be 2+2!'.format(
                len(self.BMP_reserved1), len(self.BMP_reserved2)
            )
        assert self.DIB_planes_num == 1, \
            'DIB planes number ({}) must be 1!'.format(self.DIB_planes_num)
        assert self.DIB_depth in (1, 2, 4, 8, 24), \
            'Colour depth ({}) must be in (1, 2, 4, 8, 24)!'.format(
                self.DIB_depth
            )
        assert self.DIB_comp == 0 \
            or (self.DIB_depth == 8 and self.DIB_comp == 1) \
            or (self.DIB_depth == 4 and self.DIB_comp == 2), \
            'Colour depth + compression ({}+{}) must be X+0/8+1/4+2!'.format(
                self.DIB_depth, self.DIB_comp
            )
        
        if self.DIB_depth <= 8:
            self.ppb = 8 // self.DIB_depth
            if self.palette is None:
                # Default palette is black and white or full size grey scale.
                self.DIB_num_in_plt = 2 ** self.DIB_depth
                self.palette = []
                for i in range(self.DIB_num_in_plt):
                    # Assignment that suits all: 1/2/4/8-bit colour depth.
                    s = 255 * i // (self.DIB_num_in_plt - 1)
                    self.palette.append([s, s, s])
            else:
                self.DIB_num_in_plt = len(self.palette)
        else:
            self.ppb = None
            self.DIB_num_in_plt = 0
            self.palette = None
        
        if self.pixels is None:
            self.pixels = [
                [0 if self.DIB_depth<=8 else [0,0,0] for y in range(self.DIB_h)]
                for x in range(self.DIB_w)
            ]
        
        plt_size = self.DIB_num_in_plt * 4
        self.BMP_offset = 14 + self.DIB_len + plt_size
        self.row_size = self._size_from_width(self.DIB_w)
        self.padded_row_size = self._padded_size_from_size(self.row_size)
        if self.DIB_comp == 0:
            self.DIB_raw_size = self.padded_row_size * self.DIB_h
            self.BMP_size = self.BMP_offset + self.DIB_raw_size
        
        self.initialised = True
        return self.initialised
    
    def _size_from_width(self, width):
        return (width * self.DIB_depth + 7) // 8
    
    def _padded_size_from_size(self, size):
        return (size + 3) // 4 * 4
    
    def _extract_from_bytes(self, data, index):
        # Pixel Mask
        mask = 0xFF >> (8 - self.DIB_depth)
        # One formula that suits all: 1/2/4/8-bit colour depth.
        d = data[index // self.ppb]
        return (d >> (8 - self.DIB_depth * ((index % self.ppb) + 1))) & mask
    
    def _decode_rle(self, bf_io):
        # Only bottom-up bitmap can be compressed.
        x, y = 0, self.DIB_h - 1
        while True:
            data = bf_io.read(2)
            if data[0] == 0:
                if data[1] == 0:
                    x, y = 0, y - 1
                elif data[1] == 1:
                    return
                elif data[1] == 2:
                    data = bf_io.read(2)
                    x, y = x + data[0], y - data[1]
                else:
                    num_of_pixels = data[1]
                    num_to_read = \
                        (self._size_from_width(num_of_pixels) + 1) // 2 * 2
                    data = bf_io.read(num_to_read)
                    for i in range(num_of_pixels):
                        self.pixels[x][y] = self._extract_from_bytes(data, i)
                        x += 1
            else:
                b = bytes([data[1]])
                for i in range(data[0]):
                    self.pixels[x][y] = self._extract_from_bytes(b, i%self.ppb)
                    x += 1
    
    def read_io(self, bf_io):
        """Read image from BytesIO or FileIO.
    
        :param bf_io: io object to read from.
        :type bf_io: BytesIO or FileIO.
        :returns: self.
        :rtype: MicroBMP.
        """
        # BMP Header
        data = bf_io.read(14)
        self.BMP_id = data[0:2]
        self.BMP_size = unpack('<I', data[2:6])[0]
        self.BMP_reserved1 = data[6:8]
        self.BMP_reserved2 = data[8:10]
        self.BMP_offset = unpack('<I', data[10:14])[0]
        
        # DIB Header
        data = bf_io.read(4)
        self.DIB_len = unpack('<I', data[0:4])[0]
        data = bf_io.read(self.DIB_len - 4)
        (
            self.DIB_w,
            self.DIB_h,
            self.DIB_planes_num,
            self.DIB_depth,
            self.DIB_comp,
            self.DIB_raw_size,
            self.DIB_hres,
            self.DIB_vres
        ) = unpack('<iiHHIIii', data[0:28])
        
        DIB_plt_num_info = unpack('<I', data[28:32])[0]
        DIB_plt_important_num_info = unpack('<I', data[32:36])[0]
        if self.DIB_len > 40:
            self.DIB_extra = data[36:]
        
        # Palette
        if (self.DIB_depth <= 8):
            if DIB_plt_num_info == 0:
                self.DIB_num_in_plt = 2 ** self.DIB_depth
            else:
                self.DIB_num_in_plt = DIB_plt_num_info
            self.palette = []
            for i in range(self.DIB_num_in_plt):
                data = bf_io.read(4)
                colour = [data[2], data[1], data[0]]
                self.palette.append(colour)
        
        # In case self.DIB_h < 0 for top-down format.
        if self.DIB_h < 0:
            self.DIB_h = -self.DIB_h
            is_top_down = True
        else:
            is_top_down = False
        
        self.pixels = None
        assert self.init(), \
            'Failed to initialize the image!'
        
        # Pixels
        if self.DIB_comp == 0:
            # BI_RGB
            for h in range(self.DIB_h):
                y = h if is_top_down else self.DIB_h - h - 1
                data = bf_io.read(self.padded_row_size)
                for x in range(self.DIB_w):
                    if (self.DIB_depth <= 8):
                        self.pixels[x][y] = self._extract_from_bytes(data, x)
                    else:
                        v = x * 3
                        # BMP colour is in BGR order.
                        self.pixels[x][y][2] = data[v]
                        self.pixels[x][y][1] = data[v+1]
                        self.pixels[x][y][0] = data[v+2]
        else:
            # BI_RLE8 or BI_RLE4
            self._decode_rle(bf_io)
        
        return self
    
    def write_io(self, bf_io, force_40B_DIB=False):
        """Write image to BytesIO or FileIO.
    
        :param bf_io: io object to write to.
        :type bf_io: BytesIO or FileIO.
        :param force_40B_DIB: force the size of DIB to be 40 bytes or not.
        :type force_40B_DIB: bool.
        :returns: number of bytes written to the io.
        :rtype: int.
        """
        if force_40B_DIB:
            self.DIB_len = 40
            self.DIB_extra = None
        
        # Only uncompressed image is supported to write.
        self.DIB_comp = 0
        
        assert self.init(), \
            'Failed to initialize the image!'
        
        # BMP Header
        bf_io.write(self.BMP_id)
        bf_io.write(pack("<I", self.BMP_size))
        bf_io.write(self.BMP_reserved1)
        bf_io.write(self.BMP_reserved2)
        bf_io.write(pack("<I", self.BMP_offset))
        # DIB Header
        bf_io.write(pack(
            "<IiiHHIIiiII",
            self.DIB_len,
            self.DIB_w,
            self.DIB_h,
            self.DIB_planes_num,
            self.DIB_depth,
            self.DIB_comp,
            self.DIB_raw_size,
            self.DIB_hres,
            self.DIB_vres,
            self.DIB_num_in_plt,
            self.DIB_num_in_plt
        ))
        if self.DIB_len > 40:
            bf_io.write(self.DIB_extra)
        
        # Palette
        if (self.DIB_depth <= 8):
            for colour in self.palette:
                bf_io.write(bytes([
                    colour[2]&0xFF,
                    colour[1]&0xFF,
                    colour[0]&0xFF,
                    0
                ]))
        
        # Pixels
        for h in range(self.DIB_h):
            # BMP last row comes first.
            y = self.DIB_h - h - 1
            if (self.DIB_depth <= 8):
                d = 0
                for x in range(self.DIB_w):
                    self.pixels[x][y] %= self.DIB_num_in_plt
                    # One formula that suits all: 1/2/4/8-bit colour depth.
                    d = (d << (self.DIB_depth % 8)) + self.pixels[x][y]
                    if x % self.ppb == self.ppb - 1:
                        # Got a whole byte.
                        bf_io.write(bytes([d]))
                        d = 0
                if x % self.ppb != self.ppb - 1:
                    # Last byte if width does not fit in whole bytes.
                    d <<= 8-self.DIB_depth-(x%self.ppb)*(2**(self.DIB_depth-1))
                    bf_io.write(bytes([d]))
                    d = 0
            else:
                for x in range(self.DIB_w):
                    bf_io.write(bytes([
                        self.pixels[x][y][2],
                        self.pixels[x][y][1],
                        self.pixels[x][y][0],
                    ]))
            # Pad row to multiple of 4 bytes with 0x00.
            bf_io.write(b'\x00' * (self.padded_row_size - self.row_size))
        
        num_of_bytes = bf_io.tell()
        return num_of_bytes
    
    def load(self, file_path):
        """Load image from BMP file.
    
        :param file_path: full file path.
        :type file_path: str.
        :returns: self.
        :rtype: MicroBMP.
        """
        with open(file_path, 'rb') as file:
            self.read_io(file)
        return self
    
    def save(self, file_path, force_40B_DIB=False):
        """Save image to BMP file.
    
        :param file_path: full file path.
        :type file_path: str.
        :param force_40B_DIB: force the size of DIB to be 40 bytes or not.
        :type force_40B_DIB: bool.
        :returns: number of bytes written to the file.
        :rtype: int.
        """
        with open(file_path, 'wb') as file:
            num_of_bytes = self.write_io(file, force_40B_DIB)
        return num_of_bytes
