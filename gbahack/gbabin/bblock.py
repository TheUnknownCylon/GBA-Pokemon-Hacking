
import struct
from array import array

class BBlock():
  def __init__(self):
    self.value = array('B')
    
  def addInt(self, value):
    self.value.fromstring(struct.pack("<I", value))
    
  def addShort(self, value):
    self.value.fromstring(struct.pack("<H", value))
    
  def addByte(self, value):
    self.value.fromstring(struct.pack("<B", value))
    
  def addPointer(self, value):
    self.addInt(value + 0x08000000)
    
  def toArray(self):
    return self.value
    
  @staticmethod
  def fromBytes(bytearray):
    x = BBlock()
    for b in bytearray:
      x.addByte(b)
    return x
    
