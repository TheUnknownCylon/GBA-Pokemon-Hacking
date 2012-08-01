
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

  def get(self, etype, eid):
    if etype == "person": return self.getPerson(eid)
    if etype == "sign"  : return self.getSign(eid)
    if etype == "script": return self.getScript(eid)
    raise Exception("Unknown etype")
 
  def write(self, etype, eid, script):
    if etype == "person": return self.writePerson(eid, script)
    if etype == "sign"  : return self.writeSign(eid, script)
    if etype == "script": return self.writeScript(eid, script)
    raise Exception("Unknown type")
    
  ## Thats the way (a ha a ha), I don't like it :(
  ## SCRIPT
  def scriptpointer(self, eid):
    if eid > self.numscripts:
      raise Exception("Script index too high, there are only %d scripts on this map."%self.numscripts)
    return self.pointerScripts + eid * PokeMapEventScript.size()
    
  def getScript(self, eid):
    scriptpointer = self.scriptpointer(eid)
    return PokeMapEventScript.loadFromRom(self.rom, scriptpointer)
    
  def writeScript(self, eid, script):
    scriptpointer = self.scriptpointer(eid)
    self.rom.writeArray(scriptpointer, script.toArray())

  ## PERSON
  def personpointer(self, eid):
    if eid > self.numpersons:
      raise Exception("Person index too high, there are only %d persons on this map."%self.numscripts)
    return self.pointerPersons + eid * PokeMapEventPerson.size()
    
  def getPerson(self, eid):
    p = self.personpointer(eid)
    return PokeMapEventPerson.loadFromRom(self.rom, p)
    
  def writePerson(self, eid, person):
    p = self.personpointer(eid)
    self.rom.writeArray(p, person.toArray())

  ## SIGN
  def signpointer(self, eid):
    if eid > self.numsigns:
      raise Exception("Sign index too high, there are only %d signs on this map."%self.numscripts)
    return self.pointerSigns + eid * PokeMapEventSignpost.size()
    
  def getSign(self, eid):
    p = self.signpointer(eid)
    return PokeMapEventSignpost.loadFromRom(self.rom, p)
    
  def writeSign(self, eid, sign):
    p = self.signpointer(eid)
    self.rom.writeArray(p, sign.toArray())

    

    
# ================ Below all event types are defined ========================
    
class PokeMapEventPerson(DataStruct):
  fields = [
    (RT.byte, "event"), (RT.byte, "picture"), (RT.short, "uu0"),
    (RT.short, "posx"), (RT.short, "posy"),
    (RT.byte, "talklvl"), (RT.byte, "movementtype"), (RT.byte, "movementid"), (RT.byte, "uu1"),
    (RT.byte, "trainer"), (RT.byte, "uu2"), (RT.short, "radius"),
    (RT.pointer, "scriptpointer"),
    (RT.short, "eid"), (RT.short, "uu3")
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
 
