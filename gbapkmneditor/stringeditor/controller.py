
from gbahack.gbabin.bblock import BBlock
from gbapkmneditor.gui.messages import showInfo
from gbapkmneditor.stringeditor.views import MainView, StringEditorView

from gbahackpkmn.strings import PokeString
from array import array
from gbahack.gbabin import offsetToGBA
from gbahackpkmn.pokescript.compiler import ScriptParser

class Controller():
    def __init__(self, rom, config):
        self.rom = rom
        self.stringeditor = StringEditorController(rom)
        self.mainview = MainView(self, self.stringeditor)
        
        
    def search(self, string):
        #String to bytes, strip the END OF STRING byte.
        searchbytes = PokeString(string).bytestring()[:-1]
        results = self.rom.findall(searchbytes)
        
        results_list = []
        for offset in results:
            thestr = self.rom.getRM().get(PokeString, offset)
            occ_count = len(self.rom.findall(array('B', offsetToGBA(offset))))
            results_list.append((offset, occ_count, thestr))
        
        self.mainview.setResults(results_list)
        
        
    def stringselected(self, offset):
        self.stringeditor.selectString(offset)
        
        

class StringEditorController():
    def __init__(self, rom):
        self.rom = rom
        self.parser = ScriptParser(self.rom.getScriptLang())
        self.view = StringEditorView(self)
    
    def getNumberOfPointers(self, offset):
        return len(self.rom.findall(array('B', offsetToGBA(offset))))
    
    
    def freespace(self, offset):
        return self.rom.getFreespace(offset)
    
    
    def getview(self):
        return self.view
    
    
    def selectString(self, offset):
        '''A result string has been selected. Display the selected string in the editor.'''
        thestr = self.rom.getRM().get(PokeString, offset)
        self.view.setString(offset, thestr)
    
    
    def compilestring(self, text):
        '''Converts a text to a PokeString object.'''
        #... using the Pokescript ScriptParser
        textparts = []
        for line in text.split("\n"):
            textparts.append("= %s"%line)
        
        r = PokeString()
        self.parser.parselines(textparts, r)
        return r
        
        
    def findStartpoint(self, offset):
        while offset >= 0:
            if self.rom.readByte(offset)[1] == 0xff:
                break
                
            offset -= 1
            if self.rom.find(array('B', offsetToGBA(offset)), 0) > -1:
                self.selectString(offset)
                showInfo(self.view, "Start of text found at offset 0x%X!"%offset)
                return
        
        #Very unlike to be seen.
        showInfo(self.view, "There was no valid startpoint found for the given text.")
        
        
    def save(self, offset_old, newstring, force=True):
        '''
        Saves the textstring in the given text-input.
        The caller should be sure the script does fit, data is overwritten if this is not the case.
        '''
        rm = self.rom.getRM()
        old = rm.get(PokeString, offset_old)
        rm.delete(old)
        newpointer = newstring.write(self.rom, offset_old, force)
        return newpointer
        
        
    def saveandrepoint(self, offset_old, newstring):
        offset_new = self.save(offset_old, newstring, force=False)
        
        writedata = BBlock()
        writedata.addPointer(offset_new)
        
        pointers = self.rom.findall(offsetToGBA(offset_old))
        for pointer in pointers:
            self.rom.write(pointer, writedata)

        return offset_new
        
        