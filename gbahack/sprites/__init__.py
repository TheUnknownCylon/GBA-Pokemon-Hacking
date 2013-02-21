
from gbahack.tools import lzss
from gbahack.tools import png

def readCompressedSprite(rom, offset, width, height):
    '''
    Reads an LZSS10 or LZSS11 compressed sprite from ROM.
    Returns a matrix containing palette indices.
    '''
    blob = lzss.decompress_bytes(rom.bytes[offset:])
    return _genmatrix(blob, width, height)


def readSprite(rom, offset, width, height): 
    '''
    Reads a sprite at the given pointer from the ROM.
    Returns a matrix containing palette indices.
    '''
    spritesize = int( (width * height) / 2 )  # /2: we are dealing with nibles, not bytes
    blob = rom.readBytes(offset, spritesize)[1]
    return _genmatrix(blob, width, height)


def toPNG(f, matrix, palette):
    '''
    Rewrites a given matrix (which can be the output of readSprite), to a PNG
    file. A palette should be a Palette object which could be 
    
    Note: PyPNG (https://github.com/drj11/pypng/) is required.
    '''
    
    #Rewrite the palette object to a PNG-palette
    p = palette.aslist()
    
    #write the matrix to the file-object
    w = png.Writer(len(matrix[0]), len(matrix), palette=p)
    w.write(f, matrix)
    

def _genmatrix(blob, w, h):
    '''
    Rewrite the blob to a multidimensional array representing the image.
    Blob should be an array of bytes.
    The image is build up from 8x8 pixel blocks.
    '''

    matrix = [[0] * w for _ in range(h)]
    #TODO: Find out why the following does not work:
    #  matrix = [[0] * w] * h
    
    numblocksinw = int(w / 8)
    numblocksinh = int(h / 8)
    
    #first read block 0,0; then 0,1; 0,n; 1,0; 1, 1; ... etc
    index = 0
    
    for bh in range(0, numblocksinh):
        for bw in range(0, numblocksinw):
            pmh = bh * 8 
            #read 8 pixels * 16 pixels (note: 1 byte in blob = 2 pixels)
            for _ in range(0, 8):
                pmw = bw * 8
                for _ in range(0, 4):
                    pixels = blob[index]
                    pixel_left = pixels & 0x0F
                    pixel_right = pixels >> 4
                    
                    matrix[pmh][pmw] = pixel_left
                    matrix[pmh][pmw+1] = pixel_right
                        
                    index += 1
                    pmw += 2
                pmh += 1
                
    return matrix
