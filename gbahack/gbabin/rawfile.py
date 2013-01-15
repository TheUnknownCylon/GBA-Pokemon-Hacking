import sys
import struct
from array import array
from gbahack.gbabin.bblock import BBlock

class RawFile():
    
    def __init__(self, file):
        self.file = file
        self.f = None
        self._resetfile()
    
    def __getitem__(self, v):
        return self.f[v]
    
    def _resetfile(self):
        self.f = open(self.file, 'rb').read()  #read, adjust, in binary
  
    def path(self):
        '''Returns the path of the loaded file'''
        return self.file
  
    def skip(self, offset, length):
        '''Skips reading bytes. Can be used to calculate the new pointer location.'''
        return offset + length
    
    
    def readByte(self, offset):
        '''
        Reads a byte at the given offset.
        A new pointer location and the read value are returned.
        '''
        return offset+1, self.f[offset]


    def readShort(self, offset):
        '''
        Reads a short at the given offset.
        A new pointer location and the read value are returned.
        '''
        e = offset+2
        s = self.f[offset : e]
        return e, struct.unpack('<H', s)[0]
  

    def readInt(self, offset):
        '''
        Reads an integer or long at the given offset.
        A new pointer location and the read value are returned.
        '''
        e = offset+4
        s = self.f[offset : e]
        return e, struct.unpack('<L', s)[0]
  

    def readPointer(self, offset):
        '''
        Reads a pointer from the ROM. This pointer is auto-corrected.
        (GBA ROMs have pointers with 0x08000000 added to them, these will
        be substracted)
        '''
        e, p = self.readInt(offset)
    
        if p == 0: return e, p
    
        if p > 0x08000000:
            p = p - 0x08000000
        else:
            raise Exception("Invalid pointer read from ROM")
        return e,p

    
    def readBytes(self, offset, length):
        
        ep = offset + length
        return ep, self.f[offset: ep]
  
  
    def find(self, bytes, offset):
        '''
        Finds a given bytestring, starts looking from a given offset.
        The provided bytestring should implement the buffer interface, and thus
        can be an array.array('B') instance.
        Returns the pointer for the found place in the ROM. If no pointer was found,
        -1 is returned.
        '''
        return self.f.find(bytes, offset)
    
  
    def findSpace(self, pointer, length, safe=True):
        '''
        Returns a pointer to a place in the ROM where is enough free space.
        Free space is always found in blocks of 4 bytes.
        Using the safe == True will make sure that one 0xFF is left as free space,
        so the end of the previous command may not be overwritten.
        '''
        if safe:
            p = self.find(array('B', [0x00]*(length+1)), pointer)
            if p != -1: p += 1
        else:
            p = self.find(array('B', [0x00]*length), pointer)
        return p
    
  
    def trunc(self, pointer, length, truncbyte=0xFF):
        '''Clears length bytes at a given pointer in the ROM.
        Optional trunc byte can be set.'''
        c = array('B', [truncbyte] * length)
        self.writeArray(pointer, c)
    
    
    def writeArray(self, pointer, array):
        mf = open(self.file, 'r+b')
        mf.seek(pointer)
        mf.write(array)
        mf.close()
        self._resetfile()    
  
  
    def write(self, pointer, data):
        '''Writes a bblock object to the ROM'''
        self.writeArray(pointer, data.toArray())
    
    
    def writeBlocks(self, bblockarray):
        '''Writes a dict of bblocks (accompanied by a pointer as index) to the ROM.'''
        for pointer in bblockarray:
            self.write(pointer, bblockarray[pointer])
       
