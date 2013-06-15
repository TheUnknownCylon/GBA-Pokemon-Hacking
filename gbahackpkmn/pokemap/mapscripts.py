
from gbahack import Resource
from gbahackpkmn.pokemap import MapScriptStruct
from gbahack.gbabin.datastruct import DataStruct, RomDataType as RT

class MapScripts(Resource):
    '''
    Each maps points to a MapScripts header. Here all non-event scripts
    are defined. (And things get a bit uggly here...).
    
    Access mapscripts through the public mapscripts list.
    MapScripts element data structure: (maptype, mapscript object) tuples.
    
    All first-class citizen elements of this class are currently Read Only.
    Pointers in these mapscripts can be changed and can be written back to ROM.
    '''
    
    def __init__(self, rom, p):
        self.mapscripts = []
        self.read(rom, p)
    
    def read(self, rom, p):
        self.mapscripts = []
        rm = rom.getRM()
        
        while True: #Read until end of list
            p, scripttype = rom.readByte(p)
            
            if scripttype == 0: #End of list
                break
            elif scripttype in (1, 3, 5, 6, 7):
                # [ptr] -> script
                self.mapscripts.append((scripttype, rm.get(MapScript_SimpleScript, p)))
                p, _ = rom.readPointer(p)
            elif scripttype in (2, 4):
                # [ptr] -> [var1][var2][ptr] -> script (runs when values of var1 and var2 match)
                # Note: Variables in the range 0x0000-0x3FFF contain their number.
                p, scriptheader = rom.readPointer(p)
                self.mapscripts.append((scripttype, rm.get(MapScript_ConditionalScript, scriptheader)))
            else:
                raise Exception("Unknown mapscripttype")
                

class MapScript_SimpleScript(MapScriptStruct):
    '''Simple script: is only a pointer to a script.'''
    fields = [(RT.pointer, 'scriptpointer')]


class MapScript_ConditionalScript(MapScriptStruct):
    '''Script header for scripts with two vars prepended to it.'''
    fields = [
        (RT.short, 'var1'),
        (RT.short, 'var2'),
        (RT.pointer, 'scriptpointer')
    ] 
