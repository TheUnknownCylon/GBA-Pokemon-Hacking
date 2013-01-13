
from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT


class PokeMapEvents():
    '''
    Class that deals with PokeMap Events.
    Retrieve event-objects from a ROM.
    '''
    #TODO: Retrieve warps, retrieve hidden items.

    def __init__(self, rom, eventspointertable):
        '''Initialize, header and eventspointertable.'''
        self.rom = rom
        self.rm = rom.getRM()
        self.header = self.rm.get(PokeMapEventsHeader, eventspointertable)
    
    
    def getNumberOfPersons(self):
        '''Returns the number of persons present on the map.'''
        return self.header.numpersons
    
    def getNumberOfScripts(self):
        '''Returns the number of scripts present on the map.'''
        return self.header.numscripts
    
    def getNumberOfSigns(self):
        '''Returns the number of sign posts present on the map.'''
        return self.header.numsigns
    
    def getNumberOfWarps(self):
        '''Returns the number of warps present on the map.'''
        return self.header.numwarps
    
    
    
    def getScript(self, scriptid):
        '''Returns a PokeMap Script resource.'''
        if scriptid > self.header.numscripts:
            raise Exception("Script index too high, there are only %d scripts on this map."%self.header.numscripts)
        pointer = self.header.pointerScripts + scriptid * PokeMapEventScript.size()
        return self.rm.get(PokeMapEventScript, pointer)
    
    
    def getPerson(self, personid):
        '''Returns a PokeMap Person resource.'''
        if personid > self.header.numpersons:
            raise Exception("Person index too high, there are only %d persons on this map."%self.header.numpersons)
        pointer = self.header.pointerPersons + personid * PokeMapEventPerson.size()
        return self.rm.get(PokeMapEventPerson, pointer)
    
    
    def getSign(self, signid):
        '''Returns a PokeMap sign resource.'''
        if signid > self.header.numsigns:
            raise Exception("Sign index too high, there are only %d signs on this map."%self.header.numsigns)
        pointer = self.header.pointerSigns + signid * PokeMapEventSignpost.size()
        return self.rm.get(PokeMapEventSignpost, pointer)
    
    
    def write(self, resource):
        '''Writes a retrieved resource from here back to the ROM.'''
        self.rm.store(resource)
        
    
# ================ Below all event types are defined ========================
class HiddenItemException(Exception):
    pass


class PokeMapEventsHeader(DataStruct):
    fields = [
        (RT.byte, 'numpersons'), (RT.byte, 'numwarps'), (RT.byte, 'numscripts'), (RT.byte, 'numsigns'),
        (RT.pointer, 'pointerPersons'),
        (RT.pointer, 'pointerWarps'),
        (RT.pointer, 'pointerScripts'),
        (RT.pointer, 'pointerSigns')
    ]


class PokeMapEventPerson(DataStruct):
    fields = [
        (RT.byte, "event"), (RT.byte, "spriteid"), (RT.short, "uu0"),
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
  
    def validate(self):
        if self.type > 0x04:
            raise HiddenItemException("This is not a signpost, but a hidden item!")
    
    
class PokemapHiddenItem(DataStruct):
    '''Representation of a signpost. It is not aware of its location in the ROM.'''
    fields = [
        (RT.short, "posx"), (RT.short, "posy"),
        (RT.byte, "talklvl"), (RT.byte, "type"), (RT.short, "uu0"),
        (RT.short, "itemid"), (RT.byte, "hiddenid"), (RT.byte, "amount")
    ]
  
    def validate(self):
        if self.type < 0x05:
            raise HiddenItemException("This is not a hidden item, but a signpost!")
    
    
class PokeMapEventWarp(DataStruct):
    fields = [
        (RT.short, "posx"), (RT.short, "posy"),
        (RT.byte, "talklvl"), (RT.byte, "towarpid"), (RT.byte, "map"), (RT.byte, "bank")
    ]
 
