
from gbahackpkmn.strings.pokestring import PokeString

class StringList():
    '''
    Simple class representing a list of PokeStrings in the rom.
    Reads a pre-defined amount of strings, all read Strings can be retrieved
    as Resource, as decoded text-string, or as lists.
    
    There is no storage function (yet). If there will be any, it will be placed
    here.
    '''
    
    def __init__(self, rom, offset, maxlength, count):
        self.rom = rom
        self.offset = offset
        self.maxlength = maxlength
        self.count = count
        
        self.names_resources = []
        self.names_decoded = []
        
        self._load()
        

    def getNumberOfStrings(self):
        '''Returns the number of resources stored in the StringList.'''
        return len(self.names_resources)
       
    
    def getResource(self, index):
        '''Returns a PokeString resource for the given index.'''
        return self.names_resources[index]
    
    
    def getDecodedText(self, index):
        '''Returns a decoded name for the given index.'''
        return self.names_decoded[index]
    
    
    def getAll(self):
        '''Returns a list of all PokeString resources.'''
        return self.names_resources
    
    
    def getAllDecoded(self):
        '''Returns a list of all decoded names.'''
        return self.names_decoded
    
    
    def _load(self):
        '''Internal method, loads all names from ROM.
        Also decodes them.'''
        self.names_resources = []
        self.names_decoded = []
        rm = self.rom.getRM()
        
        for stringid in range(0, self.count):
            offset = self.offset + self.maxlength * stringid
            readstring = rm.get(PokeString, offset)
            self.names_resources.append(readstring)
            self.names_decoded.append(readstring.getText())
        
    