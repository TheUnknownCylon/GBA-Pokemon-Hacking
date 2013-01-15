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
  
  '''Returns the path of the loaded file'''
  def path(self):
    return self.file
  
  
  '''Skips reading bytes. Can be used to calculate the new pointer location.'''
  def skip(self, offset, length):
    return offset + length
  

  '''Reads a byte at the given offset.
  A new pointer location and the read value are returned.'''
  def readByte(self, offset):
    return offset+1, self.f[offset]

  
  '''Reads a short at the given offset.
  A new pointer location and the read value are returned.'''
  def readShort(self, offset):
    e = offset+2
    s = self.f[offset : e]
    return e, struct.unpack('<H', s)[0]
  

  def readInt(self, offset):
    '''Reads an integer or long at the given offset.
    A new pointer location and the read value are returned.'''
    e = offset+4
    s = self.f[offset : e]
    return e, struct.unpack('<L', s)[0]
  

  def readPointer(self, offset):
    '''Reads a pointer from the ROM. This pointer is auto-corrected.
    (GBA ROMs have pointers with 0x08000000 added to them)'''
    e, p = self.readInt(offset)
    
    if p == 0: return e, p
    
    if p > 0x08000000:
      p = p - 0x08000000
    return e,p
    
    #if p & 0x08000000 != 0x08000000:
    #  raise Exception("Value %x at offset %x is not a valid pointer. " %(p, offset))
    #
    #return e, (p - 0x08000000)
  
  
  def readBytes(self, pointer, length):
    ep = pointer + length
    return ep, self.f[pointer: ep]
  
  
  def hasSpace(self, pointer, length):
    '''Returns true iff there is enough free space at the given pointer.
    Space is read in blocks of 4 bytes, all bytes have value 0xFF'''
    p = pointer
    pe = p + length
    while p < pe:
      p, v = self.readInt(p)
      #print("Reading %x with value %x" %(p, v))
      if not v == 0xFFFFFFFF:
        return False
    return True
    
  def find(self, bytes, start):
    '''
    Finds a given bytestring, starts looking from pointer start.
    The provided bytestring should implement the buffer interface, and thus
    can be an array.array('B') instance.
    Returns the pointer for the found place in the ROM. If no pointer was found,
    -1 is returned.
    '''
    return self.f.find(bytes, start)
    
  
  def findSpace(self, pointer, length, safe=True):
    '''Returns a pointer to a place in the ROM where is enough free space.
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
      
      
  def trunc(self, pointer, length):
    # I think there is a nicer way to do this
    c = []
    for _ in range(0, length):
      c.append(0xff)
    self.write(pointer, BBlock.fromBytes(c))
    
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
       
