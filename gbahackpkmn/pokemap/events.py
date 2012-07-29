
from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT

class PokeMapEvents(DataStruct):
  fields = [
    (RT.byte, 'numpersons'), (RT.byte, 'numwarps'), (RT.byte, 'numscripts'), (RT.byte, 'numsigns'),
    (RT.pointer, 'pointerPersons'),
    (RT.pointer, 'pointerWarps'),
    (RT.pointer, 'pointerScripts'),
    (RT.pointer, 'pointerSigns')
  ]
  
  def __init__(self, rom, p):
    '''rom, pointer to events table'''
    self.header = p
    self.rom = rom
    self.loadValues(rom, p)

  def get(self, type, id):
    if type == "person": return self.getPerson(id)
    if type == "sign"  : return self.getSign(id)
    if type == "script": return self.getScript(id)
    raise Exception("Unknown type")
 
  def write(self, type, id, script):
    if type == "person": return self.writePerson(id, script)
    if type == "sign"  : return self.writeSign(id, script)
    if type == "script": return self.writeScript(id, script)
    raise Exception("Unknown type")
    
  ## Thats the way (a ha a ha), I don't like it :(
  ## SCRIPT
  def scriptpointer(self, id):
    if id > self.numscripts:
      raise Exception("Script index too high, there are only %d scripts on this map."%self.numscripts)
    return self.pointerScripts + id * PokeMapEventScript.size()
    
  def getScript(self, id):
    scriptpointer = self.scriptpointer(id)
    return PokeMapEventScript.loadFromRom(self.rom, scriptpointer)
    
  def writeScript(self, id, script):
    scriptpointer = self.scriptpointer(id)
    self.rom.writeArray(scriptpointer, script.toArray())

  ## PERSON
  def personpointer(self, id):
    if id > self.numpersons:
      raise Exception("Person index too high, there are only %d persons on this map."%self.numscripts)
    return self.pointerPersons + id * PokeMapEventPerson.size()
    
  def getPerson(self, id):
    p = self.personpointer(id)
    return PokeMapEventPerson.loadFromRom(self.rom, p)
    
  def writePerson(self, id, person):
    p = self.personpointer(id)
    self.rom.writeArray(p, person.toArray())

  ## SIGN
  def signpointer(self, id):
    if id > self.numsigns:
      raise Exception("Sign index too high, there are only %d signs on this map."%self.numscripts)
    return self.pointerSigns + id * PokeMapEventSignpost.size()
    
  def getSign(self, id):
    p = self.signpointer(id)
    return PokeMapEventSignpost.loadFromRom(self.rom, p)
    
  def writeSign(self, id, sign):
    p = self.signpointer(id)
    self.rom.writeArray(p, sign.toArray())

    

    
# ================ Below all event types are defined ========================
    
class PokeMapEventPerson(DataStruct):
  fields = [
    (RT.byte, "event"), (RT.byte, "picture"), (RT.short, "uu0"),
    (RT.short, "posx"), (RT.short, "posy"),
    (RT.byte, "talklvl"), (RT.byte, "movementtype"), (RT.byte, "movementid"), (RT.byte, "uu1"),
    (RT.byte, "trainer"), (RT.byte, "uu2"), (RT.short, "radius"),
    (RT.pointer, "scriptpointer"),
    (RT.short, "id"), (RT.short, "uu3")
  ]
    
class PokeMapEventScript(DataStruct):
  fields = [
    (RT.short, "posx"), (RT.short, "posy"),
    (RT.byte, "talklvl"), (RT.byte, "uu0"), (RT.short, "varnumber"),
    (RT.short, "valvalue"), (RT.short, "uu1"),
    (RT.pointer, "scriptpointer")
  ]

class PokeMapEventSignpost(DataStruct):
  '''Representation of a signpost. It is not aware of its location in the ROM.'''
  fields = [
    (RT.short, "posx"), (RT.short, "posy"),
    (RT.byte, "talklvl"), (RT.byte, "type"), (RT.short, "uu0"),
    (RT.pointer, "scriptpointer")
  ]
  
class PokeMapEventWarp(DataStruct):
  fields = [
    (RT.short, "posx"), (RT.short, "posy"),
    (RT.byte, "talklvl"), (RT.byte, "towarpid"), (RT.byte, "map"), (RT.byte, "bank")
  ]
 
