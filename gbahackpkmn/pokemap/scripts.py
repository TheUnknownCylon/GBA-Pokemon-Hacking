from gbahack.gbabin.datastruct import DataStruct

class MapScriptStruct(DataStruct):
    '''DataStructure that contains a pointer to a PokeScript.
    
    When subclassing this class, make sure you have a field
      (RT.pointer, 'scriptpointer')
    which points to the start of a pokescript.
    '''
    pass