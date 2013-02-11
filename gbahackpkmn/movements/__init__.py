 
"""
Submodule that represent in-game movements.

TODO: Currently holder for more advanced things.
      Now only represents movements as bytestrings.
"""

from gbahack import Resource
from array import array


class Movement(Resource):
    
    name = "movement"
    
    def __init__(self, movements=None):
        '''
        Initializes the movement resource.
        Argument movement is an array.array('B') object, representing the
        bytecode moves
        '''
        movements = movements or array('B')
        self.movements = movements
        
        
    @classmethod
    def read(self, rom, pointer):
        '''
        Decompiles a set of movement instructions at the given pointer.
        Note that a movement instruction loop (should) always ends with 0xFE.
        '''
        movements = array('B')
        
        p = pointer
        while True:
            p, byte = rom.readByte(p)
            movements.append(byte)
            if byte == 0xFE: break
        
        return Movement(movements)
    
    def append(self, byte):
        self.movements.append(byte)
    
    def getMovements(self):
        return self.movements
    
    def bytestring(self):
        '''
        Returns the movement sequence as bytestring.
        If the last movement was not explictly given (with 0xFE), then this byte
        will be included implictly.
        '''
        if self.movements[-1] == 0xFE:
            return self.movements
        movements = self.movements[:]
        movements.append(0xFE)
        return movements
        