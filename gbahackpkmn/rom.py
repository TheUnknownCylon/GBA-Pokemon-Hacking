 
 
from gbahack import ROM
from gbahackpkmn.pokescript import ScriptLang

class PokemonRom(ROM):
    '''
    Pokemon ROM.
    Has initialized gbahackpkmn classes.
    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.langdef = ScriptLang()
        
        
    def getScriptLang(self):
        return self.langdef