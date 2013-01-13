 
 
from gbahack import ROM
from gbahackpkmn.pokescript import ScriptLang

class PokemonRom(ROM):
    '''
    Pokemon ROM.
    Has initialized gbahackpkmn classes.
    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #Set the correct scriptlang based on info from the metadata.
        # scriptlangdef sets the root file for loading the PokeScript definitons.
        # scriptsublang can used to only set a subset of the language.
        scriptlangdef = None
        sublang = None
        if "scriptlangdef" in self.metadata:
            scriptlangdef = self.metadata["scriptlangdef"]
        if "scriptsublang" in self.metadata:
            sublang = self.metadata["scriptsublang"]
        self.langdef = ScriptLang(scriptlangdef, sublang)
        
        
    def getScriptLang(self):
        return self.langdef