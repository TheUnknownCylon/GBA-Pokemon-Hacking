 
"""
Submodule that represent in-game movements.

TODO: Currently holder for more advanced things.
      Now only represents movements as bytestrings.
"""

from gbahack import Resource
from array import array


class Movement(Resource):
    
    def __init__(self, movements):
        '''
        Initializes the movement resource.
        Argument movement is an array.array('B') object, representing the
        bytecode moves
        '''
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
    
    
    def getMovements(self):
        return self.movements
    
    def bytestring(self):
        return self.movements
        