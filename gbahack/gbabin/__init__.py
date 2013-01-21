'''RawOps is a package which provides methods to do oparations on a binary file.'''


from gbahack.gbabin.bblock import BBlock
from gbahack.gbabin.rom import ROM

import struct

def offsetToGBA(offset):
    '''
    Converts an ROM offset to the accoring GBA offset,
    that is: add 0x08000000 and convert it to little endian.
    Returns a bytestring
    '''
    return struct.pack('<I', offset+0x08000000)
