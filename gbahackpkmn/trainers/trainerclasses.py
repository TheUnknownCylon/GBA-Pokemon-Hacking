
from gbahackpkmn.strings import StringList

class TrainerClasses():
    
    def __init__(self, rom):
        self.rom = rom
        trainerclasstable = rom.metadata['trainerclasstable']
        self.numberoftrainerclasses = rom.metadata['numtrainerclasses']
        self._names = StringList(rom, trainerclasstable, 13, self.numberoftrainerclasses)
    
    
    def getNumberOf(self):
        '''Returns the number of trainer classes in the ROM.'''
        return self.numberoftrainerclasses
    
    
    def names(self):
        '''Returns a StringList object containing all the trainer classes names.'''
        return self._names