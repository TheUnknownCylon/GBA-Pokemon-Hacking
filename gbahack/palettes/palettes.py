 
from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT
from math import floor

class Palette16(DataStruct):
  '''Representation of a palette containing 16 colours.
  Each color is represented in 5 bits red, 5 bits green, 5 bits blue.'''
  fields = [(RT.short, "color%d"%c) for c in range(0, 16) ]

  def getRGB(self, colorid):
    '''Returns a RGB tuple: contains three integers, representing the Red, Green
    and Blue values for the encoded color.'''
    c     = self.get("color%d"%colorid)
    blue   = floor(((c & (31<<10))>>10) * 255 / 31)
    green = floor(((c & (31<<5))>>5) * 255 / 31)
    red  = floor((c & 31) * 255 / 31)
    
    transparency = 0xff
    if colorid==0: transparency = 0
    
    return (red, green, blue, transparency)
  
  def aslist(self):
    return [self.getRGB(i) for i in range(0, 16)] 