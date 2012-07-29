import pprint
import struct
from array import array
from gbahackpkmn.pokescript.lang import ScriptLang, Command, ParamType, toint


class Routine():
  def __init__(self):
    self.codes = array('B')
    
  def addByte(self, byte):
    self.codes.append(byte)
    
  def addBytes(self, otherarray):
    self.codes.extend(otherarray)
  
  def overwrite(self, index, byte):
    self.codes[index] = byte
  
  def getBytes(self):
    return self.codes
  
  def length(self):
    return len(self.codes)



class Pokescript():
  def __init__(self, langdef, filename):
    self.langdef = langdef #Store the language which we are parsing
    
    self.pointerdefs = {}  #index:name, value:routine
    self.pointerrefs = []  #(routine, ref, index)
    
    self.routine = None    #holds the current parsing routine
    
    try:
      self.parse(filename)    #Parse the input
      self.validatePointers() #Make sure that all pointerrefs are correct
    except Exception as e:
      raise
      #print(" Parsing failed: "+str(e))
    
  
  def routineDef(self, name, bank=0):
    '''Get a new routine, which will be registered as a known routine.'''
    r = Routine()
    self.pointerdefs[name.lower()] = r
    return r

    
  def parse(self, filename):
    l = 0
    for line in open(filename):
      l+=1
      try: self.parseline(line)
      except Exception as e:
        raise Exception("Parsing failed at line "+str(l)+".\n "+str(line)+" "+str(e))
      
      
  def updatepointers(self, pointertable):
    for pointer in self.pointerrefs:     #For each known ref, check if there is a pointer to update
      if pointer[1] in pointertable:     #If there is an update
        self.updatepointer(pointer[0], pointer[2], pointertable[pointer[1]])
  
  def updatepointer(self, routine, offset, value):
    value += 0x08000000       #GBA pointer offset
    pointerbytes = array('B', struct.pack("<I", value))
    routine.overwrite(offset,   pointerbytes[0])
    routine.overwrite(offset+1, pointerbytes[1])
    routine.overwrite(offset+2, pointerbytes[2])
    routine.overwrite(offset+3, pointerbytes[3])

    
      
  def parseline(self, line):
    line = line.strip()
    if not line: return
    if line[0] == '\'': return #comment
    
    command = line.split(" ")[0].lower()
    args    = line.split(" ")[1:]
    
    # -- Routinedef  #org $methoddef
    if command == "#org":
      offset = args[0]
      bank = 0
      if len(args) > 1:
        bank   = args[1]
      
      if offset[0] == "$":
        self.routine = self.routineDef(offset[1:])
      else:
        raise Exception("Currently there is only support for routine definitions starting with $: e.g.: #ORG $NAME")
      return
    
    # -- Vardef
    if command == "#inline":
      raise Exception("This type of vardef is not supported at the time...")
      offset = args[1]
      bank   = args[2]
      t      = args[3]
      string = ' '.join(args[4:])
      return
    
    
    # -- Vardef  #to my understanding is this a simple routine definition.
    if command[0] == "$":
      offset = command[1:]
      bank   = args[0]
      t      = args[1]
           
      #Define a new routine. It will contain the value set in this line
      innerroutine = self.routineDef(offset)
      if t == "=": #Rewrite a string and set it as the routine content
        string = ' '.join(args[2:])
        innerroutine.addBytes(self.langdef.encodeText(string))
      elif t == ";":
        #parse the rest as a normal command
        raise Exception("Sorry, should be implemented! Is not done (yet).")
        
      return
    
    if command == "#binary":
      self.checkRoutine()
      for arg in args:
        self.routine.addByte(toint(arg))
      return
    
    #Try to find an alias for this line, if it is there, take it.
    # Only if there is no matching alias, we look for a command to match
    for alias in self.langdef.aliases:
      if alias.matches(line):
        commandargs = alias.desugar(line)
        for line in commandargs:
          self.parseline(line)
        return
      
    
    #Parse a command
    if command in self.langdef.commands:
      self.checkRoutine()
      self.handleCommand(command, args, self.routine)
      return
    
    raise Exception("Could not parse line, no rules matched: %s"%line)
        
  def validatePointers(self):
    '''This method will validate all pointers, are all pointerrefs present as pointerdefs?'''
    for pointer in self.pointerrefs:
      if not pointer[1] in self.pointerdefs:
        raise Exception("Pointer %s is not defined!"%pointer[1])
  
  
  def handleCommand(self, command, args, routine):
    commands = self.langdef.commands
    scriptcommand = commands[command]
    
    commandbytes, pointers = scriptcommand.compile(routine.length(), *args)
    for pointer in pointers:
      self.pointerrefs.append((routine, pointer[0], pointer[1]))
    routine.addBytes(commandbytes)
  
  
  def checkRoutine(self):
    if self.routine == None:
      raise Exception("No routine opened section, please create one before the actual commands by #ORG $name")
