 
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

  --directly from rom--
  sign = PokeMapEventSignpost.read(rom, pointertosignpost)
  print("X-position: %d" % sign.posx )
  
  --or via the ROMs Resource Manager (prefered)--
  sign = rom.getRM().get(PokeMapEventSignpost, pointertosignpost)
  print("X-position: %d" % sign.posx )

'''
from gbahack import Resource
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
    

class DataStruct(Resource):
  '''
  Represents a ROM data structure.
  The main inspiration of this is the C datastruct. Instead of implementing
  a full python default struct, the structure should be represented in the
  fields list. Since the DataStruct implments the abstract Resource class,
  objects can easily be read from, written to, and updated in a ROM.
  '''
  
  name = 'datastruct'
  fields = []  #Tuples of (RomDataType.type, "fieldname") pairs.

  @classmethod
  def read(cls, rom, pointer):
    '''Construction method, can be used if object is initialized from exsisting data.'''
    s = cls()
    s._loadValues(rom, pointer)
    return s
  
  def bytestring(self):
    '''Returns a binary array, containing all values set for this datablock.'''
    block = BBlock()
    for field in self.fields:
      RomDataType.appendToBlock(block, field[0], self.__getattribute__(field[1]))
    return block.toArray()


  ### End of extend methods
  
  
  def validate(self):
    '''Possible extention point. The object can validate itself based on
    expected values.'''
    pass
  
  def _loadValues(self, rom, p):
    '''(re)Load all values from the given ROM into the object.'''
    for field in self.fields:
      p, v = RomDataType.read(rom, p, field[0])
      self.__setattr__(field[1], v)
  
  def get(self, key):
    '''Returns a read field-value from the fields-array.'''
    return self.__getattribute__(key)
  

  @classmethod
  def size(cls):
    '''
    Returns the byte-size of the structure.
    This value is equal to the blength() method result, but this method also
    works on non-initialized objects.
    '''
    size = 0
    for field in cls.fields:
      size += RomDataType.size(field[0])
    return size
    
    