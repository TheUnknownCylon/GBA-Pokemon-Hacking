
from gbahackpkmn.strings import StringList

class ItemsData():
    '''
    For now, the Items class is a very simple and straightforward,
    only item names are read from the ROM, and can be retrieved. In the
    future, possibly more information on items can be loaded from ROM and
    retrieved from here.
    '''
    
    def __init__(self, rom):
        self.rom = rom
        itemstable = rom.metadata['itemstable']
        self.numberofitems = rom.metadata['numitems']
        
        #TODO: An item is not stored as a real stringlist, but along with other
        #      item meta-data. If that info will be read in later as well, this
        #      names construction should be removed.
        self._names = StringList(rom, itemstable, 11*4, self.numberofitems)


    def getNumberOf(self):
        '''Returns the number of items in the ROM.'''
        return self.numberofitems
    
    
    def namesList(self):
        '''Returns a list of decoded strings that contains all the item names.'''
        return self._names.getAllDecoded()