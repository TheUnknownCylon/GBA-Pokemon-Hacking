import shlex
import subprocess
import webbrowser
from queue import PriorityQueue

from gbahackpkmn.pokemap import PokeMapManager
from gbahackpkmn.pokescript import ScriptBurner
from gbahackpkmn.pokescript.compiler import ScriptParser
import gbahackpkmn.pokescript.script as pokescript
from gbahackpkmn.pokescript.ast import ASTCommand, ASTCollector
from gbahackpkmn.overworld import OverWorldSprites

from gbapkmneditor.tools import natsort
from gbapkmneditor.gui.messages import showInfo, showError
from gbapkmneditor.scripteditor.views import MainView

pokescriptdocuri = "https://github.com/TheUnknownCylon/GBA-Pokemon-Hacking/blob/master/docs/pokescript.md#readme"

def docuri(sublang):
    '''Returns an URI where the pokescript definition can be found for the given SubLang.'''
    return "https://github.com/TheUnknownCylon/GBA-Pokemon-Hacking/blob/master/docs/pokescript/%s.md#readme"%sublang


class Controller():
    def __init__(self, rom, config):
        '''Set up and show the main view.'''
        self.rom = rom
        self.config = config
        
        self.currentScriptgroup = None
        self.startvars = {}
        try:
            self.mapmgr = PokeMapManager(self.rom)
            self.overworld = OverWorldSprites(self.rom)
            self.mainview = MainView(self)
            self.mapchange(4, 0)
            
        except Exception as e:
            print(e)
            showError(None, 
                "There was an unexpected error, the program will quit.\n\n"+
                "Possible cautions:\n1) the opened ROM is no GBA Pokemon Game, or\n2) the"+
                "provided METADATA file is incomplete, or contains invalid values.\n\n"+
                "DEBUG information:\n"+str(e), quitapp=False)
            raise e
        
    def getOverworld(self):
        return self.overworld
    
    def showcommandslist(self):
        webbrowser.open(docuri(self.rom.getScriptLang().getSubLang()))

    def showpokescriptdoc(self):
        webbrowser.open(pokescriptdocuri)

    def mapchange(self, bankid, mapid):
        currentMap = self.mapmgr.getMap(bankid, mapid) 
        self.mainview.setScriptList(currentMap)
        
    def setScripts(self, scriptStructs):
        '''
        Sets the current script, based on the info in the scriptEvent.
        ScriptEvent should be a subclass of: gbahackpkmn.pokemap.MapScriptStruct.
        Gets a list of objects that subclass gbahackpkmn.pokemap.scripts.scriptStruct.
        '''
        
        startvars = {}
        
        #Create a scriptgroup with all structs loaded
        scriptgroup = pokescript.ScriptGroup()
        startvarname = "$start"
        
        prescript = ""
        uniqueid = 0
        
        for scriptstruct in scriptStructs:
            scriptoffset = scriptstruct.scriptpointer
            if len(scriptStructs) > 1:
                startvarname = "$start[%d]"%uniqueid
                uniqueid+=1
            
            startvars[startvarname] = scriptstruct
            if scriptoffset:
                pokescript.loadGroup(self.rom, scriptoffset, scriptgroup, startvarname)
            else:
                prescript += "'No script attatched to the selected scriptstruct %s\n"%repr(scriptstruct)
                prescript += "' If you want to attatch a script, you can uncomment the following lines:\n\n"
                prescript += "'#script %s\n"%startvarname
                prescript += "'  end\n\n"

        self.currentScriptgroup = scriptgroup
        self.startvars = startvars
        
        self.updateResources(scriptgroup)
        self.resourceSelected(('scripteditor', None))
        self.mainview.setScript(prescript+self.scriptToText(scriptgroup))
        


    def scriptToText(self, scriptgroup):
        '''
        Starts decompiling at a given pointers.
        Returns all the related scripts as a text-string.
        '''
        starts = []
        scripts = []
        others = []
        for varname in sorted(scriptgroup.getPointerlist().keys(), key=natsort):
            if varname.startswith("$start"):
                starts.append(varname)
            elif varname.startswith("$script"):
                scripts.append(varname)
            else:
                others.append(varname)
        
        text = ""
        for varname in starts + scripts + others:
            text += scriptgroup.getAST(varname).text()+"\n\n"
        
        return text
    

    def testScript(self):
        '''Try to compile the script in the sourceview.'''
        sg = self._compileandtest()
        if sg != None:
            showInfo(self.mainview, "Test OK, the script contains no errors.")
        
        
    def _compileandtest(self):
        try:
            sg = self._compile()
        except Exception as e:
            showError(self.mainview, "Compiling failed.\n\nDEBUG: "+str(e))
            raise e
            return None
            
        try:
            self._validate(sg)
        except Exception as e:
            showError(self.mainview, "There are one or multiple error in script:\n"+str(e))
            raise e
            return None
        
        return sg
    
    
    def burnScript(self):
        '''Compiles the source, if succesful updates the in-game scripts.'''
        sg = self._compileandtest()
        if sg == None:
            return
        
        try:
            try:
                pointers = self.currentScriptgroup.getPointerlist()
            except:
                pointers = {}
            rom = self.rom
            
            #set pointers in new scriptgroup related to old scriptgroup
            for varname in sg.getPointerlist():
                if varname in pointers:
                    sg.setPointer(varname, pointers[varname])
            
            print("______________________")
            print("Burning")
            b = ScriptBurner(rom)
            _ = b.burn(sg) #newpointers
            
            print("______________________")
            print("Update script pointers")
            pointerslist = sg.getPointerlist()
            for varname, resource in self.startvars.items():
                try:
                    resource.scriptpointer = pointerslist[varname]
                except:
                    resource.scriptpointer = 0
                self.rom.getRM().store(resource)
            
            print("")
            print("!! All done! Script injection was succesful!")
            self.currentScriptgroup = sg
            showInfo(self.mainview, "Script was succesfully written to the ROM.")
            
        except Exception as e:
            showError(self.mainview, "The script compiled succesfully, but writing the changes to the ROM failed.\n\nDEBUG: "+str(e))
            raise e
    
    
    def _compile(self):
        '''Compiles the Pokescript, returns a unrelated to original source scriptgroup.'''
        script = self.mainview.getScript()
        
        print("---------------------")
        print("Compiling")
        
        try:
            c = ScriptParser(self.rom.getScriptLang())
            c.parselines(script.split("\n"), None)
            print("> Compiling was succesful!")
            return c.scriptgroup()
        
        except Exception as e:
            print("> Someting went wrong:")
            print(str(e))
            raise e
    
    
    def _validate(self, scriptgroup):
        '''Validates a scriptgroup. Throws an exception if there are errors in it.'''
        #TODO: Move to somewhere else? :P
        
        import gbahackpkmn.pokescript.analysis as ana
        
        w, e = ana.analyzeScript(scriptgroup)
        errors = []
        for _, w_ in w:
            errors.append(w_)
        for _, e_ in e:
            errors.append(e_)
        
        if len(errors) > 0:
            raise Exception("\n".join(errors))
    
    
    def resourceSelected(self, data):
        rtype, value = data
        
        if rtype == "trainerbattle":
            from gbapkmneditor.trainers.controller import TrainerEditorController
            self.mainview.setEditor(TrainerEditorController(self.rom, value).getView())
        else:
            self.mainview.setEditor(None)

    
    def updateResources(self, scriptgroup):
        # Look up different kind of resources in the script
        #  Think of: TrainerBattles
        #            Movements
        #            Shop lists (TODO)
        
        trainerbattles = FindTrainerBattles()
        for astnode in scriptgroup.getASTNodes():
            astnode.collectFromASTs([trainerbattles])
        
        resources = []
        for trainerbattle in trainerbattles.getTrainerBattles():
            resources.append(("trainerbattle", trainerbattle))
        
        self.mainview.setResoursesList(resources)
        
        
    def startEmulator(self):
        '''Starts the loaded ROM in an emulator.'''
        print(self.config)
        if not 'emulator' in self.config:
            showInfo(self.mainview, "No emulator is set in the config file! Can not emulate the ROM.")
            return
        try:
            command = [x if x != "%u" else self.rom.filename for x in shlex.split(self.config['emulator'])]
            subprocess.Popen(command)
        except Exception as e:
            showError(self.mainview, "Could not start the emulator:\n"+repr(e))
        

class FindTrainerBattles(ASTCollector):
    '''A (little dirty) trainer battles finder for as ASTCollector.'''
    def __init__(self):
        self.trainerbattles = []
        
    def collect(self, astnode):
        if isinstance(astnode, ASTCommand):
            try:
                if astnode.code.signature[0].startswith("trainerbattle"):  #TODO: better trainerbattle matching
                    self.trainerbattles.append(astnode.args[0])
            except:
                pass

    def getTrainerBattles(self):
        return list(set(self.trainerbattles))
    