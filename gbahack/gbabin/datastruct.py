 
'''This file contains classes to specify data structures in ROMs.
If one knows on forehand the structure of datablob, such as a predefined fixed
sized header, extending the DataStruct class will help reading this data.

Example:
  import RomDataType as RT
  import DataStruct

  class PokeMapEventSignpost(DataStruct):
    fields = [
      (RT.short, "posx"), (RT.short, "posy"),
      (RT.byte, "talklvl"), (RT.byte, "type"), (RT.short, "uu0"),
      (RT.pointer, "scriptpointer")
    ]

  sign = PokeMapEventSignpost.loadFromRom(rom, pointertosignpost)
  print("X-position: %d" % sign.posx )
  
    
'''
from gbahack.gbabin import BBlock

class RomDataType():
  '''Class of rom datatypes. Can be used to read values from rom.'''
  byte = 0x00
  short = 0x01
  int  = 0x02
  pointer = 0x03
  
  @classmethod
  def size(cls, t):
    if t == cls.byte:    return 1
    if t == cls.short:   return 2
    if t == cls.pointer: return 4
    if t == cls.int:     return 4
    raise Exception("Wrong type!")
  
  @classmethod
  def read(cls, rom, p, t):
    '''Read: rom: rom te read, p: pointer to read, t: type to read
    Returns pointer, value tuple.'''
    if t == cls.byte:    return rom.readByte(p)
    if t == cls.short:   return rom.readShort(p)
    if t == cls.pointer: return rom.readPointer(p)
    if t == cls.int:     return rom.readInt(p)
    raise Exception("Wrong type!")
  
  @classmethod
  def appendToBlock(cls, block, t, v):
    '''Rewrites value to the correct binary, based on type t. The value is 
    appended to the datablock block.'''
    if t == cls.byte:    return block.addByte(v)
    if t == cls.short:   return block.addShort(v)
    if t == cls.pointer: return block.addPointer(v)
    if t == cls.int:     return block.addInt(v)
    

#TODO: Upgrade DataStruct to a Resource object???
class DataStruct():
  fields = []  #Tuples of (RomDataType.type, "fieldname") pairs.

  @classmethod
  def loadFromRom(cls, rom, p):
    '''Construction method, can be used if object is initialized from exsisting data.'''
    s = cls()
    s.loadValues(rom, p)
    return s
  
  def validate(self):
    '''Possible extention point. The object can validate itself based on
    expected values.'''
    pass
  
  def loadValues(self, rom, p):
    '''(re)Load all values from the given ROM into the object.'''
    for field in self.fields:
      p, v = RomDataType.read(rom, p, field[0])
      self.__setattr__(field[1], v)
  
  def get(self, key):
    '''Returns a read field-value from the fields-array.'''
    return self.__getattribute__(key)
  
  def toArray(self):
    '''Returns a binary array, containing all values set for this datablock.'''
    block = BBlock()
    for field in self.fields:
      RomDataType.appendToBlock(block, field[0], self.__getattribute__(field[1]))
    return block.toArray()
    
  
  @classmethod
  def size(cls):
    '''Returns the size of the structure.'''
    size = 0
    for field in cls.fields:
      size += RomDataType.size(field[0])
    return size
    
    