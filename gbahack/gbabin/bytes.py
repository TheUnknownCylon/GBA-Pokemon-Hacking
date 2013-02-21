import struct
from array import array

class ByteArrayReader():
    '''
    Class which represents a bytearray, and makes reading from it
    as easy as possible. Consists of methods that read a datatype from
    the bytearray, returning a new offset pointer.
    '''
    
    def __init__(self, readbytes):
        self.bytes = readbytes
        
    def skip(self, offset, length):
        '''Skips reading bytes. Can be used to calculate the new offset location.'''
        return offset + length
    
    
    def readByte(self, offset):
        '''
        Reads a byte at the given offset.
        A new offset location and the read value are returned.
        '''
        return offset+1, self.bytes[offset]


    def readShort(self, offset):
        '''
        Reads a short at the given offset.
        A new offset location and the read value are returned.
        '''
        e = offset+2
        s = self.bytes[offset : e]
        return e, struct.unpack('<H', s)[0]
  

    def readInt(self, offset):
        '''
        Reads an integer or long at the given offset.
        A new offset location and the read value are returned.
        '''
        e = offset+4
        s = self.bytes[offset : e]
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
        return ep, self.bytes[offset: ep]
  
  
    def find(self, findbytes, offset):
        '''
        Finds a given bytestring, starts looking from a given offset.
        The provided bytestring should implement the buffer interface, and thus
        can be an array.array('B') instance.
        Returns the offset for the found place in the ROM. If no offset was found,
        -1 is returned.
        '''
        return self.bytes.find(findbytes, offset)
    
    
    def findall(self, findbytes):
        '''
        Lookup all occurences of the given bytestring in the file.
        Returns a list of offsets.
        '''
        offset = 0
        results = []
        while True:
            offset = self.find(findbytes, offset)
            if offset == -1:
                break
            else:
                results.append(offset)
                offset += 1
        return results
    
  
    def findSpace(self, offset, length, safe=True):
        '''
        Returns a offset to a place in the ROM where is enough free space.
        Free space is always found in blocks of 4 bytes.
        Using the safe == True will make sure that one 0xFF is left as free space,
        so the end of the previous command may not be overwritten.
        '''
        if safe:
            p = self.find(array('B', [0x00]*(length+1)), offset)
            if p != -1: p += 1
        else:
            p = self.find(array('B', [0x00]*length), offset)
        return p
    
    
    def getFreespace(self, offset, freespacebyte=0xFF):
        '''Returns the number of free space bytes found at the given offset.'''
        #TODO: Smarter/faster implementations are possible.
        #TODO: Race condition, read until EOF
        c = 0
        while True:
            offset, byte = self.readByte(offset)
            if byte == freespacebyte:
                c += 1
            else:
                return c
        
