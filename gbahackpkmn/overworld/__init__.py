from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT
from gbahack.palettes import PaletteTable
from gbahack.sprites import readSprite, toPNG

class OverWorldSprites():
  def __init__(self, rom):
    self.rom = rom
    self.palettetablepointer = 0x3A5158
    self.spritetablepointer  = 0x3A3BB0
    self.spritepersontablepointer = 0x39FDB0
    self.palettetable = PaletteTable(rom, self.palettetablepointer)
  
  def getSprite(self, index):
    spritepointer = self.spritetablepointer + index*SpriteHeader1.size()
    return Sprite(self.rom, spritepointer, self.palettetable)
  
  def getPersonSprite(self, personid):
    _, spritepointer = self.rom.readPointer(self.spritepersontablepointer + personid*4)
    import pprint
    pprint.pprint(spritepointer)
    return Sprite(self.rom, spritepointer, self.palettetable)

class Sprite():
  def __init__(self, rom, pointer, palettetable):
    self.rom     = rom
    self.header1 = SpriteHeader1.loadFromRom(rom, pointer)
    self.header2 = SpriteHeader2.loadFromRom(rom, self.header1.pointer_spriteheader)
    self.palette = palettetable.getPalette(self.header1.paletteid)

    #Pre-calculate the size of a frame.
    # A frame is a list of nibles, each representing a palette-color index
    self.framesize = int( (self.header1.width * self.header1.height) / 2 )  # /2: we are dealing with nibles, not bytes


  def toPNG(self, frame, f):
    '''Converts a sprite to a PNG. F should be a file object opened for wb.'''
    #build a palette
    p = [self.palette.getRGB(i) for i in range(0, 16)]    
    matrix = self.getFrame(frame)
    toPNG(f, matrix, p)


  def getFrame(self, id):
    p = self.header2.pointer_sprite + id * self.framesize
    return readSprite(self.rom, p, self.header1.width, self.header1.height)

    
class SpriteHeader1(DataStruct):
  fields = [
    (RT.short, "startbytes"),
    (RT.short, "paletteid"),
    (RT.short, "paletteid_alternative"),
    (RT.short, "syncproperty"),
    
    (RT.short, "width"),  #in pixels
    (RT.short, "height"), #in pixels
    
    (RT.byte,  "unknown"), #first for bits: palette slot, other half: ??
    (RT.byte,  "Unknown"), #??
    (RT.short, "filler"),
    
    (RT.pointer, "pointer1"),
    (RT.pointer, "pointer_sizedraw"),
    (RT.pointer, "pointer_shiftredraw"),
    (RT.pointer, "pointer_spriteheader"),
    (RT.pointer, "pointer2")    
    ]
    
    
class SpriteHeader2(DataStruct):
  fields = [
    (RT.pointer, "pointer_sprite"),
    (RT.short,   "size"), #size of image/2 for VSync
    (RT.short,   "filler")
    ]