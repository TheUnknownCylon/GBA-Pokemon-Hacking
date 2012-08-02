import struct
from array import array
from gbahack.tools.numbers import toint
from gbahack.tools.numbers import toint

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
    raise Exception("Could not rewrite value: got wrong argument type: %x."%type)

      
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
      defaultvalue = None
    
  def checkParamscount(self, argscount):
    if argscount != self.neededparams:
      raise Exception("Wrong number of arguments used: got %d, expected %d."%(argscount, self.neededparams))

  def bytesignature(self): raise NotImplemented()
      
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
  
  
  def bytesignature(self):
    sig = []
    skip = 0
    for param in self.params:
      #We have to skip a param, because it was consumed with another called command
      if skip > 0:
        skip -= 1
        continue
      
      paramtype    = param[0]
      paramdefault = param[1]
      
      if paramdefault == None:
        valuestoappend = [''] * len(ParamType.rewrite(paramtype, 0))
      elif paramtype == ParamType.command:
        command = self.commands[paramdefault.lower()]
        valuestoappend = command.bytesignature()
        skip = command.neededparams
      else:
        valuestoappend = ParamType.rewrite(paramtype, paramdefault)
        
      sig += valuestoappend
    return sig  
  
  
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

  def bytesignature(self):
    sig = [self.code]
    for param in self.params:
      paramtype    = param[0]
      paramdefault = param[1]
      if paramdefault == None:
        valuestoappend = [''] * len(ParamType.rewrite(paramtype, 0))
      else:
        valuestoappend = ParamType.rewrite(paramtype, paramdefault)
      sig += valuestoappend
      
    return sig
    
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
    