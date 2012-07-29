
class ScriptBurner():
  
  def __init__(self, rom):
    self.rom = rom
  
  
  def burn(self, script):
    '''This method prepares burning the routines, it will find free space in the
    ROM, and set all script pointers correctly.'''
    rom = self.rom
    startpointer = rom.findSpace(0x800000, self.calcsize(script))
    
    #Calculate the startpointers
    # so we can update the in-script pointers
    offset = 0
    pointers = {}
    for routine in script.pointerdefs:
      pointers[routine] = startpointer+offset
      offset += script.pointerdefs[routine].length()
    script.updatepointers(pointers)
    
    #Now do the actual burn
    scriptpointers = {}
    for pointername in pointers:
      r = script.pointerdefs[pointername]
      p = pointers[pointername]
      rom.writeArray(p, r.getBytes())
      print(" Written $%s to #%x"%(pointername, p))
      scriptpointers[pointername] = p
    
    return scriptpointers
    
    
  def calcsize(self, script):
    s = 0
    for routine in script.pointerdefs:
      s += script.pointerdefs[routine].length()
    return s