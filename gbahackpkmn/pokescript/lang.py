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
#  -  addcmmd <command name> <command code> ' [description]
#  -  alias <command alias> ' [description]
#  -  addparm <size> [data] ' [description]

import os
import sys

from array import array
from gbahack.tools.numbers import toint
from gbahackpkmn.pokescript.langcommands import *
from gbahackpkmn.strings import PokeString

class ScriptLang():
  '''This class represents the language in a structured way. All defines can be
  found here. Also all commands and aliases are in this class. These values are
  read from the language definition files.'''
  def __init__(self, startfile=None):
    self.commands = {}
    self.aliases  = []
    self.defines  = {}

    if startfile==None:
      startfile = os.path.dirname(sys.modules[__name__].__file__) + "/langdef/includes.psh"
    self.handleInclude(startfile)
    
    
    
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
        self.defines[instructions[1].lower()] = toint(instructions[2])
      elif instruction[0:len("addcmmd")] == "addcmmd":
        commandname = instructions[1].lower()
        commandcode = toint(instructions[2])
        lastcommand = Command(commandname, commandcode, self.defines)
        self.commands[commandname] = lastcommand
      elif instruction == "alias":
        lastcommand = Alias(' '.join(instructions[1:]), self.commands)
        self.aliases.append(lastcommand)
      elif instruction == "addparm":
        defaultvalue = None
        instructiontype = int(instructions[1])

        if len(instructions) > 2:
          try: defaultvalue = toint(instructions[2])
          except:
            if   instructions[2][0:4] == "bind": pass    #TODO: Restriction
            elif instructions[2][0:7] == "select(":
              select = instructions[2][8:-1].split(",")
              defaultvalue = SELECT(select)
              
            elif instructions[2][0:5] == "mask(":        #format: mask(number)
              defaultvalue = toint(instructions[2][5:-1])
            elif instructiontype == ParamType.command:
              defaultvalue = instructions[2] 
            else:
              raise Exception("Unknown default value for param: "+repr(instructions[2]))
            
        lastcommand.addParam(instructiontype, defaultvalue)
    return lastcommand
  
  def handleInclude(self, filename):
    '''Include a separate file with commands. Note that file includes are relative to the
    file to be included.'''
    mypath = os.getcwd()
    try: os.chdir(os.path.dirname(filename))
    except: pass

    try: self.parse(os.path.basename(filename))
    except Exception as e: raise
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
  
