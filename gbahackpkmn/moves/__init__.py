
from gbahackpkmn.strings import StringList

class MovesData():
    
    def __init__(self, rom):
        self.rom = rom
        movenamestable = rom.metadata['movenamestable']
        self.numberofmoves = rom.metadata['nummoves']
        self._names = StringList(rom, movenamestable, 13, self.numberofmoves)


    def getNumberOf(self):
        '''Returns the number of moves in the ROM.'''
        return self.numberofmoves
    
    
    def names(self):
        '''Returns a StringList object containing all the move names.'''
        return self._names
