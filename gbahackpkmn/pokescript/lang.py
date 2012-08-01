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
import pprint

import os
import sys
import struct
from array import array

def toint(v):
  '''Tries to convert a value to int if possible.
  Possible decodings are just the integer as string or int,
   or a hex-string: toint("#10"), will return 0x10 (or 16)'''
  try: return int(v)
  except: pass
  
  if len(v) > 1 and v[0] == '#':
    try: return int('0x'+v[1:], 16)
    except: pass
  
  if len(v) > 2 and v[0:2].lower() == '0x':
    try: return int(v, 16)
    except: pass
    
  if len(v) > 2 and v[0:2].lower() == '&h':
    try: return int(v[2:], 16)
    except: pass
    
  raise Exception("Could not convert value to number: "+repr(v))

    
class ParamType:
  '''Represents all allowed parameter types'''
  byte    = 0x00
  word    = 0x01
  int     = 0x02
  pointer = 0x03
  eos     = 0x04 #end of script
  command = 0x07 #name of command to call
  pointer_text = 0x08
  pointer_movement = 0x09
  
  @staticmethod
  def ispointer(type):
    if type == ParamType.pointer: return True
    if type == ParamType.pointer_text: return True
    if type == ParamType.pointer_movement: return True
    return False
  
  @staticmethod
  def rewrite(type, value):
    if type == ParamType.byte:
      return struct.pack("<B", value)
    elif type == ParamType.word:
      return struct.pack("<H", value)
    elif ParamType.ispointer(type) or type == ParamType.int:
      return struct.pack("<I", value)

      
class SELECT():
  def __init__(self, options):
    self.options = options
    
  def get(self, i):
    return self.options[i]

    
class CodeCommand():
  def __init__(self):
    self.params = []
    self.neededparams = 0
    self.endofscript = False
    
  def addParam(self, paramtype, defaultvalue=None):
    '''Adds a parameter to the command. Note that values without a default
    are the values that should be set by the user.'''
    
    #Pokescript does some additional footers which are not required!
    if paramtype == ParamType.eos:
      self.endofscript = True
      return
      
    self.params.append((paramtype, defaultvalue))
    
    if defaultvalue == None or isinstance(defaultvalue, SELECT):
      self.neededparams+=1
  
  def checkParamscount(self, argscount):
    if argscount != self.neededparams:
      raise Exception("Wrong number of arguments used: got %d, expected %d."%(argscount, self.neededparams))

  
      
class Alias(CodeCommand):
  '''An alias is a shortcut definition for several commands and arguments.
  An alias can not be compiled, but can be desugared. This means that
  the alias is rewritten to the commands it actually represents. These lines
  can then be parsed as normal commands.'''
  def __init__(self, string, commands):
    CodeCommand.__init__(self)
    self.signature = string.lower().split()
    self.commands = commands #pointer to list of all commands, needed for desugaring
    
  def matches(self, line):
    try: self.stripParams(line)
    except: return False
    return True
    
  def stripParams(self, matchstr):
    params = []
    match = matchstr.lower().split()   
    if len(match) != len(self.signature): raise Exception("Not a match!")
    
    for i in range(0, len(self.signature)):
      if self.signature[i][0] == "$":
        params.append(match[i])
      elif self.signature[i] != match[i]: raise Exception("Not a match!")
    
    return params
  
  def desugar(self, line):
    params = self.stripParams(line)
    return self.desugar_helper(params)
    
 
  def desugar_helper(self, args):
    argstaken = 0
    paramstaken = 0
    lines = []
    params = self.params
    
    while paramstaken < len(params):
      p = params[paramstaken]
      paramstaken+=1

      ptype  = p[0]
      pvalue = p[1]
      if ptype == ParamType.command:  #param type
        command = self.commands[pvalue.lower()]
        cline = pvalue.lower() + " "
        for i in range(0, command.neededparams):
          value = params[paramstaken][1]
          paramstaken += 1

          if value == None:
            value =  args[argstaken]
            argstaken += 1
          elif isinstance(value, SELECT):
            value = value.get(toint(args[argstaken]))
            argstaken += 1
          else: #make sure value is a string
            value = str(value)
          
          cline += value  
          cline += " "
          
        lines.append(cline)

      else:
        cline = "#BINARY "
        x = ParamType.rewrite(ptype, pvalue)
        for y in x:
          cline += "%d "%y
        
        lines.append(cline)
        
    return lines

      
class Command(CodeCommand):
  def __init__(self, name, code, constants):
    '''Binary code which the command represents. Constants holds a list of
    all defines, i.e. constants.'''
    CodeCommand.__init__(self)
    self.name = name
    self.code = code
    self.constants = constants
      
  def compile(self, inneroffset, *args):
    self.checkParamscount(len(args))
    
    usedargs = 0
    
    pointers = []
    bytes = array('B')
    bytes.append(self.code)
    
    for param in self.params:  #param[0]: paramtype, param[1]: param default value
      value = None
      if param[1] == None:
        value = args[usedargs]
        usedargs += 1
        
      elif isinstance(param[1], SELECT):
        value = param[1].get(args[usedargs])
        usedargs += 1
        
      else:
        value = param[1]

      if ParamType.ispointer(param[0]):
        pointer = value
        if pointer[0] != "$": raise Exception("Only Pointers to $ are supported yet!")
        value = 0 #we can not determine the pointer yet, write something: write 0!
        pointers.append((pointer[1:].lower(), inneroffset+len(bytes)))
      else:
        try: value = toint(value)
        except: #value may not be an integer, but may be a (defined) constant!
          value = value.lower()
          if value in self.constants:
            value = self.constants[value]
          else:
            raise Exception("The given parameter could not be converted to integer and is also not defined as a constant.\n"+repr(value))
        
      bytes.fromstring(ParamType.rewrite(param[0], value))
    
    return bytes, pointers
    

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
      elif instruction == "addcmmd":
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
    if char in self.texthashinv: return "[%s]"%texthashinv(char)
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
  
