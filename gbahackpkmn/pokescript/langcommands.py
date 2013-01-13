import struct
from array import array
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
  
  @classmethod
  def rewrite(cls, type, value):
    try:
      return cls.rewritehelper(type, value)
    except:
      raise Exception("Could not rewrite value %s of type %X."%(repr(value), type))
  
  @staticmethod
  def rewritehelper(type, value):
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
    self.description = ""
    self.argdescriptions = []
    
  def setDescription(self, description):
    self.description = description
  
  def getDescription(self):
    return self.description

  def getArgDescription(self, i):
    return self.argdescriptions[i]
    
  def addParam(self, paramtype, defaultvalue=None, description=None):
    '''
    Adds a parameter to the command. Note that values without a default
    are the values that should be set by the user.
    '''
    
    #Pokescript does some additional footers which are not required!
    if paramtype == ParamType.eos:
      self.endofscript = True
      return
      
    self.params.append((paramtype, defaultvalue))
    self.argdescriptions.append(description)
    
    if defaultvalue == None or isinstance(defaultvalue, SELECT):
      self.neededparams+=1
      defaultvalue = None
  
  def getParam(self, i):
      return self.params[i]
  
  def getNumberOfParams(self):
    return self.neededparams
  
  def checkParamscount(self, argscount):
    if argscount != self.neededparams:
      raise Exception("Wrong number of arguments used: got %d, expected %d."%(argscount, self.neededparams))

  def compile(self, *args):
    '''Compiles the command according to a list of arguments.'''
    raise NotImplementedError()

  def bytesignature(self):
    '''
    Returns the byte signature for the given CodeCommand, argument slots
    are left empty.
    '''
    raise NotImplementedError()

      
class Alias(CodeCommand):
  '''An alias is a shortcut definition for several commands and arguments.
  An alias can not be compiled, but can be desugared. This means that
  the alias is rewritten to the commands it actually represents. These lines
  can then be parsed as normal commands.'''
  def __init__(self, string, commands):
    CodeCommand.__init__(self)
    self.signature = string.lower().split()
    self.commands = commands #pointer to list of all commands, needed for desugaring
    self._bytesig = None
    
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
    if self._bytesig == None:
      self._bytesig = self._generate_signature()
    return self._bytesig
    
    
  def _generate_signature(self):
    sig = []
    skip = 0
    for paramindex in range(0, len(self.params)):
      param = self.params[paramindex]
      
      #We have to skip a param, because it was consumed with another called command
      if skip > 0:
        skip -= 1
        continue
      
      paramtype    = param[0]
      paramdefault = param[1]
      
      if paramdefault == None:
        valuestoappend = [''] * len(ParamType.rewrite(paramtype, 0))
      elif paramtype == ParamType.command:
        currentparamindex = paramindex + 1
        command = self.commands[paramdefault.lower()]
        
        commandefaultargs = []
        for parami in range(0, command.neededparams):
          parami_default = self.params[currentparamindex + parami][1]
          if parami_default == None: commandefaultargs.append(None)
          else: commandefaultargs.append(parami_default)
        
        valuestoappend = command.bytesignature(*commandefaultargs)
        skip = command.neededparams
      else:
        valuestoappend = ParamType.rewrite(paramtype, paramdefault)
        
      sig += valuestoappend
    return sig  
  
  def compile(self, *args):
    #print("+++++ Compiling Alias "+repr(self.getParam(0)))
    compiled = array('B')
    
    argstaken = 0
    paramstaken = 0
    params = self.params
    
    while paramstaken < len(params):
      p = params[paramstaken]
      paramstaken+=1

      ptype  = p[0]
      pvalue = p[1]
      if ptype == ParamType.command:  #param type
        command = self.commands[pvalue.lower()]
        commandargs = []
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
          
          commandargs.append(value)
        
        #print(">>>> "+repr(commandargs))
        compiled.extend(command.compile(*commandargs))

      else:
        x = ParamType.rewrite(ptype, pvalue)
        for y in x:
          compiled.append(y)
        
    return compiled

      
class Command(CodeCommand):
  def __init__(self, name, code, constants):
    '''Binary code which the command represents. Constants holds a list of
    all defines, i.e. constants.'''
    CodeCommand.__init__(self)
    self.name = name
    self.code = code
    self.constants = constants
    self.signature = [self.name]
    
  def addParam(self, paramtype, defaultvalue=None, description=None):
    super().addParam(paramtype, defaultvalue, description)
    if defaultvalue == None and paramtype != ParamType.eos:
      self.signature.append("$%d"%len(self.signature))

  def bytesignature(self, *args):
    '''Returns the commands byte signature. It is possible to
    set expected values, by providing an *args array with default values'''
    sig = [self.code]
    argstaken = 0
    for param in self.params:
      paramtype    = param[0]
      paramdefault = param[1]
      
      if paramdefault == None and argstaken < len(args):
        paramdefault = args[argstaken]
        argstaken += 1

      if isinstance(paramdefault, SELECT):
        paramdefault = None
        
      if paramdefault == None:        
        valuestoappend = [''] * len(ParamType.rewrite(paramtype, 0))
      else:
        valuestoappend = ParamType.rewrite(paramtype, paramdefault)
      sig += valuestoappend
      
    return sig
    
    
  def compile(self, *args):
    #print("Compile "+repr(self.code)+" with args "+repr(args))
    self.checkParamscount(len(args))
       
    usedargs = 0
    
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

      try:
        value = toint(value)
      except: #value may not be an integer, but may be a (defined) constant!
        try:
          value = value.lower()
          if value in self.constants:
            value = self.constants[value]
          else:
            raise Exception()
        except:
          raise Exception("The given parameter could not be converted to integer and is also not defined as a constant: "+repr(value))
        
      bytes.fromstring(ParamType.rewrite(param[0], value))
    
    return bytes
    