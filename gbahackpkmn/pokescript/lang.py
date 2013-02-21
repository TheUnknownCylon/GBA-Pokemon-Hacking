# Loads the script lang, important note! Takes no indention into account!
# Stupid and quick implementation, does not follow good compiler strategies,
#  but prolly no one is going to use this!
# Note that I did not set up this definition myself! Search for PokeAdv.exe or Rubicon.
#
# Definition:
#  Normalizing: the parser normalizes the string, tabs are replaced with spaces,
#               multiple spaces are normalized to one space
#               
#  Comments:
#   - block:   start line with /*
#              end line with */
#   - lineend: '
#
#  Commands:
#  -  #include <file>          includes file
#  -  #define <name> <values>  define a key with given values
#  -  #(different)             ignored
#  -  addcmmd[gameslist] <command name> <command code> ' [description]
#           where gamelist can be one or multiple of the following: [frlg][e][rs]
#  -  alias <command alias> ' [description]
#  -  addparm <size> [data] ' [description]


import os
import sys
import re

from gbahack.tools.numbers import toint
from gbahackpkmn.strings import PokeString
from gbahackpkmn.pokescript.langcommands import ParamType, Command, Alias


class ScriptLang():
    '''
    This class represents the language in a structured way. All defines can be
    found here. Also all commands and aliases are in this class. These values are
    read from the language definition files.
    '''
    def __init__(self, startfile=None, sublang=None, rom=None):
        '''
        Optional argument rom: if rom is set, several defines will be loaded
        from it, such as pokemon names, item names, etc.
        '''
        self.sublang = sublang
        
        self.commands = {}
        self.aliases  = []
        self.defines  = {}

        if startfile==None:
            startfile = os.path.join(os.path.dirname(sys.argv[0]), "gbahackpkmn", "pokescript", "langdef", "includes.psh")
        self.handleInclude(startfile)
        
        if rom:
            self.loadDefinesFromRom(rom)
    
    def loadDefinesFromRom(self, gamerom):
        '''It is possible to load defines from a pokemon game rom.
        Call this method with the rom as argument.'''
        # Load all values from ROM, remove spaces (easier parsing later on)
        self.defines['pkmn'] = [x.replace(' ', '').upper() for x in gamerom.pokemondata.names().getAllDecoded()]
        self.defines['move'] = [x.replace(' ', '').upper() for x in gamerom.movesdata.names().getAllDecoded()]
        self.defines['item'] = [x.replace(' ', '').upper() for x in gamerom.itemsdata.namesList()]
    
        ##Renice the 0th elements, in-game these values are "?????", but
        ## in this langdef they will represented as "NONE"
        self.defines['pkmn'][0] = "NONE"
        self.defines['move'][0] = "NONE"
        self.defines['item'][0] = "NONE"
    
    def getDefines(self, definestype):
        try:
            return self.defines[definestype]
        except:
            print("No defines found for: %s"%definestype)
            return {}
        
    
    def getSubLang(self):
            '''Returns the sublang the ROM uses.'''
            return self.sublang
        
    def parse(self, filename):
        lastcommand = None
        
        comment = False
        for line in open(filename, encoding="iso-8859-15"):
            #normalize the line
            line.replace("\t", " ")
            line = line.strip()
            line = ' '.join(line.split())

            if not line: continue
            if len(line) > 2 and line[0:2] == "/*":
                comment = True
            if comment == True and len(line) > 2 and line[-2:] == "*/":
                comment = False
            if comment: continue #Still in command parsing, skip line
            
            try: 
                lastcommand = self.parseline(line, lastcommand)
            except:
                print("Could not parse line from langdef: %s"%line)
                raise Exception("Could not parse line from langdef: %s"%line)

    def parseline(self, line, lastcommand):
        if True:
            instructions = line.split('\'')[0].strip().split(" ")
            instructions = list(map(lambda x: x.strip(), instructions))
            instruction  = instructions[0].lower()
            
            if instruction == "#include":
                self.handleInclude(instructions[1])
                
            elif instruction == "#define":
                deftype = instructions[1]
                defkey  = instructions[2].upper()
                defval  = toint(instructions[3])
                if not deftype in self.defines:
                    self.defines[deftype] = {}
                self.defines[deftype][defval] = defkey
                
            elif instruction[0:len("addcmmd")] == "addcmmd":
                commandname = instructions[1].lower()
                commandcode = toint(instructions[2])
                lastcommand = Command(commandname, commandcode, self.defines)
                lastcommand.setDescription(stripDescription(line))
                
                #Only store commands of interest for future reference, but keep
                # lastcommand to append its args to (otherwise they are appended to
                # the wrong arg)
                sublangs = re.findall(r"\[([^\]]*)\]", instruction[len("addcmmd"):])
                if len(sublangs)==0 or self.sublang in sublangs:
                    self.commands[commandname] = lastcommand
                         
            elif instruction == "alias":
                lastcommand = Alias(' '.join(instructions[1:]), self.commands)
                lastcommand.setDescription(stripDescription(line))
                self.aliases.append(lastcommand)
                
            elif instruction == "addparm":
                defaultvalue = None
                instructiontype = int(instructions[1].split(":")[0])
                try:
                    definevaluestype = instructions[1].split(":")[1].strip().lower()
                except:
                    definevaluestype = None

                if len(instructions) > 2:
                    try: defaultvalue = toint(instructions[2])
                    except:
                        if instructions[2][0:4] == "bind":
                            pass #TODO: Restriction
                            
                        elif instructions[2][0:5] == "mask(": #format: mask(number)
                            defaultvalue = toint(instructions[2][5:-1])
                        elif instructiontype == ParamType.command:
                            defaultvalue = instructions[2] 
                        else:
                            raise Exception("Unknown default value for param: "+repr(instructions[2]))
                
                lastcommand.addParam(instructiontype, defaultvalue, definevaluestype=definevaluestype, description=stripDescription(line))
        return lastcommand
    
    
    def handleInclude(self, filename):
        '''Include a separate file with commands. Note that file includes are relative to the
        file to be included.'''
        mypath = os.getcwd()
        try: os.chdir(os.path.dirname(filename))
        except: pass

        try: self.parse(os.path.basename(filename))
        except Exception as e: raise e
        finally: os.chdir(mypath)
        
    
    def getCommand(self, code):
        '''Get a command for the given code.'''
        for commandname in self.commands:
            command = self.commands[commandname]
            if command.code == code:
                return command
        raise Exception("No command with code %x"%code)
    
    
    def encodeText(self, text):
        return PokeString(text).bytestring()
    

    def getCommands(self):
        return self.commands

    def getAliases(self):
        return self.aliases


def stripDescription(line):
    descriptionstart = line.find("'")
    if descriptionstart != -1:
        return line[descriptionstart+1:]
    else:
        return None
        