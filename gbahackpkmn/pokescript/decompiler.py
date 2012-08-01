from gbahackpkmn.pokescript.lang import ParamType

class Decompiler():
  def __init__(self, langdef, rom):
    self.langdef = langdef
    self.rom = rom

class EndOfScript(Exception):
  def __init__(self, commandline):
    self.commandline = commandline
  
class DecompileTypes:
  POKESCRIPT = 0x00
  STRING     = 0x01
  MOVEMENT   = 0x02
    
class DecompileJob():
  
  def __init__(self, langdef, rom, scriptpointer):
    self.langdef = langdef
    self.rom = rom
    
    #Store all compiled scripts
    self.routines = {}
    
    #queue of scripts to decompile.
    self.pointerqueue = {scriptpointer: DecompileTypes.POKESCRIPT} 
    
    while len(self.pointerqueue) > 0:
      pointer = list(self.pointerqueue.keys())[0]
      type = self.pointerqueue.pop(pointer)
      
      #Do not decompile already decompiled routines
      if pointer in self.routines: continue

      if type == DecompileTypes.POKESCRIPT:
        routine = self.decompileRoutine(pointer)
      elif type == DecompileTypes.STRING:
        routine = self.decompileString(pointer)
      elif type == DecompileTypes.MOVEMENT:
        routine = self.decompileMovement(pointer)
      else: raise Exception("BUG! No such routine type.")

      self.routines[pointer] = routine
    
    
  def queue(self, pointer, type):
    '''Add a script pointer to the queue of scripts to be decompiled.'''
    self.pointerqueue[pointer] = type
 
 
  def decompileString(self, pointer):
    '''Decompiles a String from the ROM. Note that we assume that
    a String always ends with 0xFF, which is the case in Pokemon games.'''
    p = pointer
    text = ""
    while True:
      p, byte = self.rom.readByte(p)

      if byte == 0xFF: break
      
      try: text += self.langdef.decodeChar(byte)
      except: text += "?"
      
    return ["#ORG 0x%X"%pointer, "= %s"%text]

    
  def decompileMovement(self, pointer):
    '''Decompiles a set of movement instructions at the given pointer.
    Note that a movement instruction loop (should) always ends with 0xFE.'''
    p = pointer
    instructions = ""
    
    while True:
      p, byte = self.rom.readByte(p)
      instructions += "0x%x"%byte +" "
      if byte == 0xFE: break
      
    return ["#ORG 0x%X"%pointer, "; %s"%instructions]

  def decompileRoutine(self, pointer):
    '''Decompiles a script from the ROM at the given pointer.'''
    routine = ["#ORG 0x%X"%pointer]
    
    p = pointer
    while True:
      try:
        p, commandline = self.decompileCommand(p)
        routine.append(commandline)
      except EndOfScript as e:
        routine.append(e.commandline)
        break
      except Exception as e:
        raise
      
    return routine
   
   
  def decompileCommand(self, p):
    '''Decompiles the command at the given pointer, also parses the parameters.'''
    p, instruction = self.rom.readByte(p)
        
    try:
      command = self.langdef.getCommand(instruction)
    except:
      return p, "#raw 0x%x"%instruction
      
    commandline = "%s "%command.name
    
    for param in command.params:
      paramtype    = param[0]
      paramdefault = param[1]
      
      if paramtype == ParamType.byte:
        p, value = self.rom.readByte(p)
        
      elif paramtype == ParamType.word:
        p, value = self.rom.readShort(p)
        
      elif ParamType.ispointer(paramtype):
        p, value = self.rom.readPointer(p)
        if paramtype == ParamType.pointer_text:
          self.queue(value, DecompileTypes.STRING)  
        elif paramtype == ParamType.pointer_movement:
          self.queue(value, DecompileTypes.MOVEMENT)
        else:
          self.queue(value, DecompileTypes.POKESCRIPT)
          
      elif ParamType == ParamType.int:
        p, value = self.rom.readInt(p)
      
      #human parameter to add
      if paramdefault == None:
        commandline += "0x%x "%value
      
      else:    #in the other case we can check wheter the expected value 
        pass   # matches the real value
        
    if command.endofscript == True:
      raise EndOfScript(commandline)
    
    return p, commandline