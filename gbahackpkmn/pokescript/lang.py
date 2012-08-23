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
#  -  #addHash <hash> <value>  text hash, replace this complete thing with values in a text-string
#  -  #addText <char> <value>  text letter rewrite to hex
#  -  #(different)             ignored
#  -  addcmmd <command name> <command code> ' [description]
#  -  alias <command alias> ' [description]
#  -  addparm <size> [data] ' [description]

import os
import sys

from array import array
from gbahack.tools.numbers import toint
from gbahackpkmn.pokescript.langcommands import *


class ScriptLang():
  '''This class represents the language in a structured way. All defines can be
  found here. Also all commands and aliases are in this class. These values are
  read from the language definition files.'''
  def __init__(self, startfile=None):
    self.commands = {}
    self.aliases  = []
    self.texthash = {}
    self.text     = {}
    self.defines  = {}

    if startfile==None:
      startfile = os.path.dirname(sys.modules[__name__].__file__) + "/langdef/includes.psh"
    self.handleInclude(startfile)
    
    #Store the inverse of the text-tables, for faster lookup
    self.texthashinv = dict(zip(self.texthash.values(),self.texthash))
    self.textinv = dict(zip(self.text.values(),self.text))
    
    
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
      elif instruction == "#addhash":
        self.texthash[instructions[1]] = toint(instructions[2])
      elif instruction == "#addtext":
        char = instructions[1]
        if len(char) > 1: char = chr(toint(char))  #If char is represented as a number, rewrite
        self.text[char] = toint(instructions[2])
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
  
  
  def decodeChar(self, char):
    if char == 0x00: return " "  #special case
    if char in self.texthashinv:
      print("DECODE SPECIAL CHAR: "+repr(char))
      return "%s"%self.texthashinv[char]
    try: return self.textinv[char]
    except: raise Exception("Can not decode text char %X (not defined)."%char)
    
    
  def encodeText(self, text):
    textarray = array('B')
    
    i = 0
    while i < len(text):
      char = text[i]
      i+=1
      
      if char == "[":
        ctrl = "["
        while i < len(text): #read until ]
          char = text[i]
          i+=1
          ctrl += char
          if char == "]":
            print("Looking up: %s"%ctrl)
            if ctrl.lower() in self.texthash:
              textarray.append(self.texthash["\\v"])
              textarray.append(self.texthash[ctrl])
            else:
              textarray.append(self.text["?"])
              textarray.append(self.text["?"])
              textarray.append(self.text["?"])
            break
       
      elif char == "\\":
        nextchar = text[i]
        i+=1
        char = ""+char+nextchar
        if char in self.texthash:
          textarray.append(self.texthash[char])
        else:
          textarray.append(0x00)
      
      else: #normal char to print
       if char not in self.text:
         textarray.append(0x00)
       else:
         textarray.append(self.text[char])
    
    textarray.append(0xff)
    return textarray
  
