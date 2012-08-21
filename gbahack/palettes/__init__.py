
from gbahack.palettes.palettes import Palette16
from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT

class PaletteTable():
  '''Class which represents a palette table in a GBA ROM.
  One get a palette with the getPalette method, which takes a palette id as
  argument. 
  
  NOTE: Currently only 16 colour palettes are supported.'''
  def __init__(self, rom, pointer):
    self.rom = rom
    self.pointer = pointer
    self.palettes = {}
    self.loadPalettes()
    
  def loadPalettes(self):
    self.palettes = {}
    p = self.pointer
    while True:
      paletteinfo = PaletteEntry.loadFromRom(self.rom, p)
      if(paletteinfo.palettepointer == 0x00): break
      self.palettes[paletteinfo.paletteid] = paletteinfo.palettepointer      
      p += PaletteEntry.size()
      
  def getPalette(self, paletteid):
    '''Loads and returns a palette from the ROM.'''
    palletpointer = self.palettes[paletteid]
    return Palette16.loadFromRom(self.rom, palletpointer)
    
    
class PaletteEntry(DataStruct):
  '''Represents an entry in the palette table.'''
  fields = [
    (RT.pointer, "palettepointer"),
    (RT.short,   "paletteid"),
    (RT.short,   "filler")
    ]